import hashlib
import uuid
from typing import Iterator, List, Optional, Sequence, Tuple, Union

from langchain_core.stores import BaseStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.models import Filter
from langchain_core.documents import Document


def create_uuid_from_string(val: str) -> str:
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))


class QdrantDocStore(BaseStore[str, Document]):
    """BaseStore implementation using Qdrant as the backend.

    Examples:
        Create a QdrantDocStore instance and perform operations on it:

        .. code-block:: python

            # Instantiate the QdrantDocStore with a Qdrant client
            from qdrant_client import QdrantClient
            self.qdrant = QdrantClient("http://localhost:6333")
            qdrant_doc_store = QdrantDocStore(qdrant_client, collection_name="test-collection")

            # Set values for keys
            doc1 = Document(...)
            doc2 = Document(...)
            qdrant_doc_store.mset([("key1", doc1), ("key2", doc2)])

            # Get values for keys
            values = qdrant_doc_store.mget(["key1", "key2"])
            # [doc1, doc2]

            # Iterate over keys
            for key in qdrant_doc_store.yield_keys():
                print(key)

            # Delete keys
            qdrant_doc_store.mdelete(["key1", "key2"])
    """

    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
    ) -> None:
        """Initialize a Qdrant doc store.

        Args:
            qdrant_client (QdrantClient): Qdrant client instance.
            collection_name (str): collection name to use
        """
        if not collection_name:
            raise ValueError("collection_name must be provided.")

        self.client = client
        self.collection_name = collection_name

    def create_schema(self, delete_existing: bool = False) -> None:
        if delete_existing and self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                self.collection_name,
                vectors_config={},
                # TODO: at some point we might want to have embeddings on document summaries
                # vectors_config=
                # VectorParams(size=1024, distance=Distance.COSINE),
            )

    def mget(self, keys: Sequence[str]) -> List[Optional[Document]]:
        """Get the list of documents associated with the given keys.

        Args:
            keys (list[str]): A list of keys representing Document IDs..

        Returns:
            list[Document]: A list of Documents corresponding to the provided
                keys, where each Document is either retrieved successfully or
                represented as None if not found.
        """
        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[create_uuid_from_string(key) for key in keys],
            with_payload=True,
            with_vectors=False,
            timeout=10,
        )
        return [
            Document(
                id=point.payload["metadata"]["source"],
                page_content=point.payload["page_content"],
                metadata=point.payload["metadata"],
            )
            for point in points
            if point is not None and point.payload is not None
        ]

    def mset(self, key_value_pairs: Sequence[Tuple[str, Document]]) -> None:
        """Set the given key-value pairs.

        Args:
            key_value_pairs (list[tuple[str, Document]]): A list of id-document
                pairs.
        Returns:
            None
        """
        self.client.upsert(
            self.collection_name,
            points=[
                PointStruct(
                    id=create_uuid_from_string(k),
                    payload={
                        "metadata": v.metadata,
                        "page_content": v.page_content,
                    },
                    vector={},
                )
                for k, v in key_value_pairs
            ],
        )

    def mdelete(self, keys: Sequence[str]) -> None:
        """Delete the given ids.

        Args:
            keys (list[str]): A list of keys representing Document IDs..
        """
        self.client.delete(
            self.collection_name, [create_uuid_from_string(key) for key in keys]
        )

    def yield_keys(self, *, prefix: Optional[str] = None) -> Iterator[str]:
        """Yield keys in the store.

        Args:
            prefix (str): prefix of keys to retrieve.
        """
        raise NotImplementedError("Not implemented yet")
        # we need to know which field the ID is in, where to pass this in best? constructor?
        # offset = 0
        # while offset is not None:
        #    points, offset = self.client.scroll(self.collection_name, with_payload=True, with_vectors=False, offset=offset)
        #    for point in points:
        #        yield str(uuid.UUID(hex=point.id)

    def yield_documents(self, filter: Optional[Filter] = None) -> Iterator[Document]:
        """Yield documents in the store."""
        offset = 0
        while offset is not None:
            points, offset = self.client.scroll(
                self.collection_name,
                with_payload=True,
                with_vectors=False,
                offset=offset,
                scroll_filter=filter,
            )
            for point in points:
                if point is not None and point.payload is not None:
                    yield Document(
                        id=point.payload["metadata"]["source"],
                        page_content=point.payload["page_content"],
                        metadata=point.payload["metadata"],
                    )
