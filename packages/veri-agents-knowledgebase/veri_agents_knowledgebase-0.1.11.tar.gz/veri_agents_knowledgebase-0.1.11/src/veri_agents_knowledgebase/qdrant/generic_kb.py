import logging
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional

from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import models

from veri_agents_knowledgebase.knowledgebase import (
    DataSource,
    DocumentLoader,
    KnowledgeFilter,
    RWKnowledgebase,
)
from veri_agents_knowledgebase.qdrant.qdrant_kb import QdrantKnowledgebase
from veri_agents_knowledgebase.qdrant.summarization import Summarizer

log = logging.getLogger(__name__)


class GenericDocumentLoader(DocumentLoader):
    def __init__(self, data_source: DataSource):
        """Generic document loader that loads documents from a location."""
        super().__init__(data_source)

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=200
        )
        self.embed_model_id = (
            "sentence-transformers/all-MiniLM-L6-v2"  # TODO: change this
        )
        self.chunker = HybridChunker(tokenizer=self.embed_model_id)  # pyright: ignore[reportArgumentType]

    def _split(self, text: str, metadata: dict):
        doc = Document(page_content=text, metadata=metadata)
        new_docs = self.splitter.split_documents([doc])
        return new_docs

    def _add(
        self,
        parent_doc: Document,
        docs: List[Document],
        text: str,
        fieldname: str | None,
        metadata: dict,
    ):
        if text:
            if fieldname:
                parent_doc.page_content += f"{fieldname}: {text}\n"
            else:
                parent_doc.page_content += f"{text}\n"
            new_docs = self._split(text, metadata)
            docs.extend(new_docs)

    def load_documents(
        self, **kwargs
    ) -> Iterator[tuple[Document, list[Document] | None]]:
        data_location_path = Path(self.data_source.location)

        if data_location_path.is_file():
            files = [str(data_location_path)]
        else:
            files = [
                str(file) for file in data_location_path.rglob("*") if file.is_file()
            ]

        if len(files) == 0:
            raise FileNotFoundError(f"No files found at {data_location_path}")

        doc_converter = DocumentConverter()

        for f in files:
            log.info(f"Processing {f}")
            parent_result = doc_converter.convert(source=f)

            doc_name = Path(f).name
            doc_location = Path(f).relative_to(self.data_source.location).parent
            parent_doc = Document(
                page_content=parent_result.document.export_to_markdown(
                    image_placeholder=""
                ),
                metadata={
                    "source": f"{self.data_source.name}::{doc_name}::{doc_location}",
                    "data_source": self.data_source.name,
                    "doc_name": doc_name,
                    "doc_location": doc_location,
                    "last_updated": datetime.now().isoformat(),
                    "tags": self.data_source.tags,
                },
            )
            chunk_iter = self.chunker.chunk(parent_result.document)
            child_docs = [
                Document(
                    page_content=self.chunker.serialize(chunk=chunk),
                    metadata={
                        **chunk.meta.export_json_dict(),
                        "data_source": self.data_source.name,
                        "tags": self.data_source.tags,
                    },
                )
                for chunk in chunk_iter
            ]
            yield parent_doc, child_docs


class GenericQdrantKnowledgebase(QdrantKnowledgebase, RWKnowledgebase):
    """A generic knowledgebase that can be used to index and retrieve documents
    from various sources."""

    def __init__(
        self,
        vectordb_url: str,
        embedding_model: Embeddings,
        filter: KnowledgeFilter | None = None,
        llm: BaseLanguageModel | None = None,
        data_sources: List[DataSource | DocumentLoader] | None = None,
        embed_summary: bool = False,
        **kwargs,
    ):
        """ Initialize the generic knowledgebase.

        Args:
            vectordb_url (str): The URL of the vector database.
            embedding_model (Embeddings): The embedding model to use for indexing.
            filter (KnowledgeFilter | None): Optional filter to apply to the knowledgebase.
            llm (BaseLanguageModel | None): Optional language model for summarization and tagging.
            data_sources (List[DataSource | DocumentLoader] | None): List of data sources or document loaders to index.
            embed_summary (bool): Whether to embed the summary of documents as another child document.
            **kwargs: Additional keyword arguments for the knowledgebase.
        """
        super().__init__(
            vectordb_url=vectordb_url,
            embedding_model=embedding_model,
            filter=filter,
            data_sources=data_sources,
            **kwargs,
        )
        self.llm = llm
        self.doc_summarize = self.metadata.doc_summarize
        self.doc_autotag = self.metadata.doc_autotag
        self.embed_summary = embed_summary
        self.id_key = "source"  # key to use for the document ID in the docstore

        if self.doc_summarize:
            if self.llm is None:
                raise ValueError("LLM required for summarization")
            self.summarizer = Summarizer(
                self.llm,
                summarize=self.doc_summarize,
                tags=self.metadata.tags if self.doc_autotag else None,
            )

    def process_doc(self, parent_doc: Document, child_docs: List[Document]):
        """Process a document before indexing, this includes summarization and potential other steps."""
        if self.doc_summarize or self.doc_autotag:
            summary, tags = self.summarizer(
                f"Document: {parent_doc.metadata['source']}\nContent: {parent_doc.page_content}\nUser tags: {', '.join(parent_doc.metadata['tags'] if 'tags' in parent_doc.metadata else [])}\n"
            )
            parent_doc.metadata["summary"] = summary
            if tags:
                log.debug(f"Predicted tags for {parent_doc.metadata['source']}: {tags}")
                current = set(parent_doc.metadata["tags"])
                current.update(tags)
                parent_doc.metadata["tags"] = list(current)
                for cd in child_docs:
                    cd.metadata["tags"] = list(current)
            log.info(
                f"Summarized {parent_doc.metadata['source']} to {summary}, set tags to {parent_doc.metadata['tags'] if 'tags' in parent_doc.metadata else []}"
            )
            if self.embed_summary and "summary" in parent_doc.metadata:
                # Add a summary as a child document
                content = f"{parent_doc.metadata.get('title', '')}\n"
                content += parent_doc.metadata.get("summary", "")
                doc = Document(
                    page_content=content,
                    metadata=parent_doc.metadata.copy(),
                )
                doc.metadata["summary"] = True
                child_docs.append(doc)

    async def _aindex(self, data_source: DataSource | DocumentLoader):
        # we don't support async indexing yet
        return self._index(data_source)

    def _delete_data_source(self, data_source: DataSource):
        """Delete all documents for a given data source."""
        log.info(f"Deleting all documents for data source {data_source.name}")
        self.qdrant.delete(
            self.docs_collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.data_source",
                            match=models.MatchValue(value=data_source.name),
                        )
                    ]
                )
            ),
            wait=True,
        )
        self.qdrant.delete(
            self.chunks_collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.data_source",
                            match=models.MatchValue(value=data_source.name),
                        )
                    ]
                )
            ),
            wait=True,
        )

    def _index(self, data_source: DataSource | DocumentLoader):
        loader, data_source = self._acquire_loader(data_source, GenericDocumentLoader)
        log.info(f"Indexing {loader.data_source.name} ({loader.data_source.location})")

        docs = loader.load_documents()

        # if data source is not incremental, first delete all existing documents of this data source
        if not data_source.incremental:
            self._delete_data_source(data_source)

        # one yield is one article consisting fo multiple documents
        for parent_doc, child_docs in docs:
            if not parent_doc or not child_docs:
                continue

            # set tags and data source if not yet set
            if data_source.tags and "tags" not in parent_doc.metadata:
                parent_doc.metadata["tags"] = data_source.tags
                for cd in child_docs:
                    cd.metadata["tags"] = data_source.tags
            if "data_source" not in parent_doc.metadata:
                parent_doc.metadata["data_source"] = data_source.name
                for cd in child_docs:
                    cd.metadata["data_source"] = data_source.name

            # retrieve existing document and compare
            parent_doc_id = parent_doc.metadata["source"]
            existing_docs = self.doc_store.mget([parent_doc_id])
            if len(existing_docs) > 0:
                existing_doc = existing_docs[0]
                # TODO: shall we store hashes or use timestamps?
                # Once we start ingesting images we should probably do this check
                # in parsedocs already :(
                if (
                    data_source.incremental
                    and existing_doc
                    and existing_doc.page_content == parent_doc.page_content
                ):
                    log.info(f"Document {parent_doc_id} already indexed, skipping")
                    continue
                else:
                    log.info(f"Document {parent_doc_id} changed, deleting old data")

                    # unfortunately the langchain abstraction can't do a filtered delete
                    result = self.qdrant.delete(
                        self.chunks_collection_name,
                        points_selector=models.FilterSelector(
                            filter=models.Filter(
                                must=[
                                    models.FieldCondition(
                                        key="metadata.source",
                                        match=models.MatchValue(value=parent_doc_id),
                                    )
                                ]
                            )
                        ),
                        wait=True,
                    )
                    log.info(f"Deleting {parent_doc_id}  children result: {result}")
                    # chunks deleted, now delete the doc itself
                    self.doc_store.mdelete([parent_doc_id])

            # additional processing like summarization we only do if the doc changed
            log.info(f"Processing document {parent_doc_id}")
            self.process_doc(parent_doc, child_docs)

            log.info(f"Indexing document {parent_doc_id}")

            # add the documents to the stores
            for doc in child_docs:
                doc.metadata[self.id_key] = parent_doc.metadata[self.id_key]
            self.vector_store.add_documents(child_docs)
            self.doc_store.mset([(parent_doc.metadata[self.id_key], parent_doc)])

    def set_tags(
        self,
        doc_id: str,
        tags: list[str],
    ):
        """Sets tags for a document."""
        self.qdrant.set_payload(
            collection_name=self.chunks_collection_name,
            points=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=doc_id),
                    )
                ]
            ),
            payload={"tags": tags},
            key="metadata",
            wait=False,
        )

        self.qdrant.set_payload(
            collection_name=self.docs_collection_name,
            points=models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.source",
                        match=models.MatchValue(value=doc_id),
                    )
                ]
            ),
            payload={"tags": tags},
            key="metadata",
            wait=False,
        )

        self._load_tags.cache_clear() # pyright: ignore[reportAttributeAccessIssue]
