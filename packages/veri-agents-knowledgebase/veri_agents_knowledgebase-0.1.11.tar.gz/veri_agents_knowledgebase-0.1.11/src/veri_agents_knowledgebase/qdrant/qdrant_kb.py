import logging
from typing import Any, AsyncGenerator, Iterator, cast

import cachetools.func
from langchain_core.tools import BaseTool
from langchain_core.embeddings import Embeddings
from langchain_core.messages.utils import count_tokens_approximately
from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient, models
from qdrant_client.models import Filter
from qdrant_client.models import Distance, VectorParams
from veri_agents_knowledgebase.knowledgebase import (
    Knowledgebase,
    KnowledgeFilter,
    and_filters,
)
from veri_agents_knowledgebase.qdrant.qdrant_doc_store import QdrantDocStore
from veri_agents_knowledgebase.tools.knowledge_retrieval import (
    FixedKnowledgebaseListDocuments,
    FixedKnowledgebaseRetrieveDocuments,
    FixedKnowledgebaseWithTagsQuery,
)
from veri_agents_knowledgebase.types import Document, DocumentChunks, DocumentReference, ScoredDocument, ScoredDocumentChunk, ScoredDocumentChunks

log = logging.getLogger(__name__)


class QdrantKnowledgebase(Knowledgebase):
    def __init__(
        self,
        vectordb_url: str,
        embedding_model: Embeddings,
        filter: KnowledgeFilter | None = None,
        retrieve_summaries: bool = True,
        retrieve_parents: bool = True,
        retrieve_parents_max_tokens: int = 10000,
        retrieve_parents_num: int = 3,
        retrieve_total_tokens: int = 70000,
        **kwargs,
    ):
        """Initialize the Qdrant knowledge base.
        
        Args:
            vectordb_url (str): The URL of the Qdrant vector database.
            embedding_model (Embeddings): The embedding model to use for vectorization.
            filter (KnowledgeFilter | None): Optional filter to apply to the knowledge base.
            retrieve_summaries (bool): Whether to retrieve summaries of documents and add them to the context.
            retrieve_parents (bool): Whether to retrieve parent documents of retrieved chunks.
            retrieve_parents_max_tokens (int): Maximum tokens for retrieving parent documents, otherwise chunks are used.
            retrieve_parents_num (int): Number of parent documents to retrieve, the ones with top relevancy scores will be selected.
            retrieve_total_tokens (int): Total tokens limit for retrieval.
        """
        super().__init__(**kwargs)
        self.chunks_collection_name = f"chunks_{self.metadata.collection}"
        self.docs_collection_name = f"docs_{self.metadata.collection}"
        self.filter = filter
        self.retrieve_summaries = retrieve_summaries
        self.retrieve_parents = retrieve_parents
        self.retrieve_parents_max_tokens = retrieve_parents_max_tokens
        self.retrieve_parents_num = retrieve_parents_num
        self.retrieve_total_tokens = retrieve_total_tokens

        self.embedding_model = embedding_model

        log.info(f"Connecting to Qdrant at {vectordb_url}")
        self.qdrant = QdrantClient(vectordb_url)
        self._init_collection()
        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.vector_store = QdrantVectorStore(
            client=self.qdrant,
            collection_name=self.chunks_collection_name,
            # FIXME
            embedding=self.embedding_model,  # pyright: ignore[reportArgumentType]
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_embedding=sparse_embeddings,
            sparse_vector_name="sparse",
        )
        self.doc_store = QdrantDocStore(
            client=self.qdrant, collection_name=self.docs_collection_name
        )
        self.doc_store.create_schema()

    def _init_collection(self):
        if not self.qdrant.collection_exists(self.chunks_collection_name):
            self.qdrant.create_collection(
                self.chunks_collection_name,
                vectors_config={
                    "dense": VectorParams(
                        size=1024, distance=Distance.COSINE
                    )  # TODO get size from somewhere
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams(),
                },
            )

    @cachetools.func.ttl_cache(maxsize=1, ttl=360)
    def _load_tags(self):
        """Load tags from the documents in the knowledge base."""
        tags = self.metadata.tags
        for doc in self.doc_store.yield_documents():
            if doc.metadata and "tags" in doc.metadata:
                doc_tags = doc.metadata["tags"]
                if isinstance(doc_tags, str):
                    doc_tags = [doc_tags]
                for doc_tag in doc_tags:
                    if doc_tag not in tags:
                        tags[doc_tag] = ""
        return tags

    @property
    def tags(self):
        """Get the tags for the workflow."""
        return self._load_tags()

    def search(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ) -> Iterator[DocumentChunks | Document]:
        # for now let's do naive retrieval
        qdrant_filter = self._create_qdrant_filter(and_filters(filter, self.filter))
        log.debug("Qdrant Filter: %s", qdrant_filter)
        qdrant_chunks = self.vector_store.similarity_search_with_score(
            query, k=limit, filter=qdrant_filter
        )
        if not qdrant_chunks:
            return iter([])
        
        # Find all documents with the same parent ID and then sort by documents with most chunks plus score
        ret: list[ScoredDocumentChunks | ScoredDocument] = []
        subdocs_per_doc: dict[str, ScoredDocumentChunks] = {}
        for d, score in qdrant_chunks:
            if "source" in d.metadata:
                id = d.metadata["source"]
                parent = DocumentReference(id=id, metadata=d.metadata)
                doc_chunks = subdocs_per_doc.setdefault(id, ScoredDocumentChunks(id=parent.id, metadata=parent.metadata, chunks=[]))

                # TODO: add score
                doc_chunks.chunks.append(ScoredDocumentChunk(chunk_content=d.page_content, score=score, metadata=d.metadata))

        # Get all scores and select the top n parent documents
        top_parent_docs = sorted(
            subdocs_per_doc.items(),
            key=lambda item: item[1].total_score,
            reverse=True,
        )[: self.retrieve_parents_num]
        top_parent_doc_ids = [doc_id for doc_id, _ in top_parent_docs]

        # Now for each parent document, retrieve the full document
        for parent_id, doc_chunks in subdocs_per_doc.items():
            parent_docs = self.doc_store.mget([parent_id])
            if parent_docs and parent_docs[0]:
                parent_doc = parent_docs[0]

                # Check if document is too long, then either attach the full document or just the chunks
                if (self.retrieve_parents and
                      (count_tokens_approximately([parent_doc.page_content]) < self.retrieve_parents_max_tokens) and
                      parent_id in top_parent_doc_ids):
                    ret.append(ScoredDocument.from_doc(parent_doc, score=doc_chunks.total_score))
                else:
                    ret.append(doc_chunks)

        return iter(ret)
        
    def list_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[DocumentReference]:
        qdrant_filter = self._create_qdrant_filter(and_filters(filter, self.filter))
        return iter([DocumentReference(id=cast(str, doc.id), metadata=doc.metadata) for doc in self.doc_store.yield_documents(filter=qdrant_filter)])

    async def alist_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[DocumentReference, None]:
        """Get all documents from the knowledge base."""
        qdrant_filter = self._create_qdrant_filter(filter)
        for doc in self.doc_store.yield_documents(filter=qdrant_filter):
            yield DocumentReference(id=cast(str, doc.id), metadata=doc.metadata)

    def get_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[Document]:
        qdrant_filter = self._create_qdrant_filter(and_filters(filter, self.filter))
        return self.doc_store.yield_documents(filter=qdrant_filter)

    async def aget_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Get all documents from the knowledge base."""
        qdrant_filter = self._create_qdrant_filter(filter)
        for doc in self.doc_store.yield_documents(filter=qdrant_filter):
            yield doc

    def get_tools(
        self,
        search_tools: bool = True,
        list_tools: bool = True,
        retrieve_tools: bool = True,
        write_tools: bool = False,
        name_suffix: str | None = None,
        runnable_config_filter_prefix: str | None = None,
        **kwargs: Any,
    ) -> list[BaseTool]:
        """Get agent tools to access this knowledgebase.

        Args:
            search_tools (bool): Whether to include tools for searching documents.
            list_tools (bool): Whether to include tools for listing documents.
            retrieve_tools (bool): Whether to include tools for retrieving documents.
            write_tools (bool): Whether to include tools for writing documents.
        Returns:
            list[BaseTool]: List of tools for the knowledge base.
        """
        tools = []
        if search_tools:
            tools.append(
                FixedKnowledgebaseWithTagsQuery(
                    knowledgebase=self,
                    num_results=kwargs.get("num_results", 10),
                    name_suffix=f"_{self.metadata.collection if name_suffix is None else name_suffix}",
                    runnable_config_filter_prefix=runnable_config_filter_prefix or "filter_",
                )
            )
        if list_tools:
            tools.append(
                FixedKnowledgebaseListDocuments(
                    knowledgebase=self,
                    name_suffix=f"_{self.metadata.collection if name_suffix is None else name_suffix}",
                    runnable_config_filter_prefix=runnable_config_filter_prefix or "filter_",
                )
            )
        if retrieve_tools:
            tools.append(
                FixedKnowledgebaseRetrieveDocuments(
                    knowledgebase=self,
                    name_suffix=f"_{self.metadata.collection if name_suffix is None else name_suffix}",
                    runnable_config_filter_prefix=runnable_config_filter_prefix or "filter_",
                )
            )
        return tools

    def _create_qdrant_filter(
        self,
        filter: KnowledgeFilter | None = None,
    ):
        """Create a Qdrant filter from the knowledgebase filter.
        Args:
            filter (KnowledgeFilter): The knowledge filter to convert.
        Returns:
            Filter: The Qdrant filter.
        """
        if not filter:
            return None

        must = []
        # doc filter means all the documents in the list (so a should clause)
        if filter.docs:
            doc_filter = filter.docs
            if isinstance(filter.docs, str):
                doc_filter = [filter.docs]
            should = []
            for doc_id in doc_filter:
                should.append(
                    models.FieldCondition(
                        key="metadata.source", match=models.MatchValue(value=doc_id)
                    )
                )
            must.append(Filter(should=should))
        if filter.tags_any_of:
            tag_any_filter = filter.tags_any_of
            if isinstance(filter.tags_any_of, str):
                tag_any_filter = [filter.tags_any_of]
            should = []
            for tag in tag_any_filter:
                should.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
            must.append(Filter(should=should))
        if filter.tags_all_of:
            tag_all_filter = filter.tags_all_of
            if isinstance(filter.tags_all_of, str):
                tag_all_filter = [filter.tags_all_of]
            for tag in tag_all_filter:
                must.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
        if filter.pre_tags_any_of:
            pre_tag_any_filter = filter.pre_tags_any_of
            if isinstance(filter.pre_tags_any_of, str):
                pre_tag_any_filter = [filter.pre_tags_any_of]
            should = []
            for tag in pre_tag_any_filter:
                should.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
            must.append(Filter(should=should))
        if filter.pre_tags_all_of:
            pre_tag_all_filter = filter.pre_tags_all_of
            if isinstance(filter.pre_tags_all_of, str):
                pre_tag_all_filter = [filter.pre_tags_all_of]
            for tag in pre_tag_all_filter:
                must.append(
                    models.FieldCondition(
                        key="metadata.tags",
                        match=models.MatchValue(value=tag),
                    )
                )
        return Filter(must=must) if must else None
