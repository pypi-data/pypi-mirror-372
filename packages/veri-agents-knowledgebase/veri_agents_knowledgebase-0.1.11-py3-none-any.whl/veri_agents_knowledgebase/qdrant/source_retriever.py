import uuid
from typing import Any, List, Optional, Sequence, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter

from langchain.retrievers import MultiVectorRetriever


class SourceDocumentRetriever(MultiVectorRetriever):
    """ Retrieve small chunks and return the full source document.

    This is a special case of the ParentDocumentRetriever but we don't want
    a full parent doc to be split into chunks but we already have chunks 
    available due to the structured nature of the data we got.

            )
    """  # noqa: E501

    parent_splitter: Optional[TextSplitter] = None
    """The text splitter to use to create parent documents.
    If none, then the parent documents will be the raw documents passed in."""

    child_metadata_fields: Optional[Sequence[str]] = None
    """Metadata fields to leave in child documents. If None, leave all parent document 
        metadata.
    """

    def add_documents(
        self,
        parent_document: Document,
        child_documents: List[Document],
        ids: Optional[List[str]] = None,
        add_to_docstore: bool = True,
        **kwargs: Any,
    ) -> None:
        """Adds documents to the docstore and vectorstores.

        Args:
            documents: List of documents to add
            ids: Optional list of ids for documents. If provided should be the same
                length as the list of documents. Can be provided if parent documents
                are already in the document store and you don't want to re-add
                to the docstore. If not provided, random UUIDs will be used as
                ids.
            add_to_docstore: Boolean of whether to add documents to docstore.
                This can be false if and only if `ids` are provided. You may want
                to set this to False if the documents are already in the docstore
                and you don't want to re-add them.
        """
        for doc in child_documents:
            doc.metadata[self.id_key] = parent_document.metadata[self.id_key]
        self.vectorstore.add_documents(child_documents, **kwargs)
        if add_to_docstore:
            self.docstore.mset([(parent_document.metadata[self.id_key], parent_document)])

    # async def aadd_documents(
    #     self,
    #     documents: List[Document],
    #     ids: Optional[List[str]] = None,
    #     add_to_docstore: bool = True,
    #     **kwargs: Any,
    # ) -> None:
    #     docs, full_docs = self._split_docs_for_adding(documents, ids, add_to_docstore)
    #     await self.vectorstore.aadd_documents(docs, **kwargs)
    #     if add_to_docstore:
    #         await self.docstore.amset(full_docs)