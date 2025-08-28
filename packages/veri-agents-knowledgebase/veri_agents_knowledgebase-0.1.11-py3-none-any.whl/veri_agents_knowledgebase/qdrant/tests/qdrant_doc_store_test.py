import unittest

from qdrant_client import QdrantClient
from langchain_core.documents import Document

from veri_agents_knowledgebase.qdrant.qdrant_doc_store import QdrantDocStore


# test for QdrantDocStore
class QdrantDocStoreTest(unittest.TestCase):
    def setUp(self):
        self.qdrant = QdrantClient("http://localhost:6668")
        self.qdrant_doc_store = QdrantDocStore(
            self.qdrant, collection_name="test_qdrantdoc"
        )
        self.qdrant_doc_store.create_schema(delete_existing=True)

    def test_add(self):
        input_doc = Document(
            page_content="The great cow walked over the lazy dog",
            metadata={"source": "somesource"},
        )
        input_doc2 = Document(
            page_content="The lazy dog jumped over the great cow",
            metadata={"source": "somesource2"},
        )
        self.qdrant_doc_store.mset([("somesource", input_doc)])
        docs = self.qdrant_doc_store.mget(["somesource"])
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].page_content, input_doc.page_content) # pyright: ignore[reportOptionalMemberAccess]
        self.qdrant_doc_store.mset([("somesource2", input_doc2)])
        docs = self.qdrant_doc_store.mget(["somesource", "somesource2"])
        self.assertEqual(len(docs), 2)
        self.qdrant_doc_store.mdelete(["somesource", "somesource2"])
        docs = self.qdrant_doc_store.mget(["somesource", "somesource2"])


if __name__ == "__main__":
    unittest.main()
