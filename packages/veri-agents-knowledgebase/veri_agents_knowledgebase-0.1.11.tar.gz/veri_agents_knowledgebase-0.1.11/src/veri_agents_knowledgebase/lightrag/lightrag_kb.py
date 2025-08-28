import asyncio
import json
import logging
import os
from contextvars import ContextVar
from datetime import datetime
from functools import partial
from os import PathLike
from pathlib import Path
from typing import Any, AsyncGenerator, Iterator, List, Optional, cast

import asyncpg
import lightrag.operate as operate
from docling.document_converter import DocumentConverter
from langchain_core.tools import BaseTool
from lightrag import LightRAG, QueryParam
from lightrag.base import DocStatus
from lightrag.kg.postgres_impl import ClientManager, PGGraphStorage, PostgreSQLDB
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.hf import hf_embed
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import EmbeddingFunc, always_get_an_event_loop
from transformers import AutoModel, AutoTokenizer
from veri_agents_knowledgebase.knowledgebase import (
    DataSource,
    DocumentLoader,
    DataSourceOrLoader,
    Graph,
    GraphEdge,
    GraphKnowledgebase,
    GraphNode,
    KnowledgeFilter,
    RWGraphKnowledgebase,
    SubGraph,
)
from veri_agents_knowledgebase.lightrag.lightrag_tools import LightRAGQuery
from veri_agents_knowledgebase.tools.knowledge_retrieval import (
    FixedKnowledgebaseListDocuments,
    FixedKnowledgebaseRetrieveDocuments,
)
from langchain_core.documents import Document

log = logging.getLogger(__name__)

# We have to monkey patch LightRAG so we can use multiple DBs
current_db_name: ContextVar[str] = ContextVar("current_db_name", default="default")
original_lock = ClientManager._lock
ClientManager._instances = {}
ClientManager._lock = original_lock or asyncio.Lock()


async def _get_client_patched(cls):
    db_name = current_db_name.get()

    async with cls._lock:
        if db_name not in cls._instances:
            config = cls.get_config()
            config["database"] = db_name
            db = PostgreSQLDB(config)
            await db.initdb()
            await db.check_tables()
            cls._instances[db_name] = {"db": db, "ref_count": 1}
        else:
            cls._instances[db_name]["ref_count"] += 1
        return cls._instances[db_name]["db"]


async def _release_client_patched(cls, db: PostgreSQLDB):
    db_name = current_db_name.get()

    async with cls._lock:
        entry = cls._instances.get(db_name)
        if entry and entry["db"] is db:
            entry["ref_count"] -= 1
            if entry["ref_count"] == 0:
                if db.pool is not None:
                    await db.pool.close()
                del cls._instances[db_name]


# Monkey patch
ClientManager.get_client = cast(classmethod, classmethod(_get_client_patched))  # type: ignore[assignment]
ClientManager.release_client = cast(classmethod, classmethod(_release_client_patched))  # type: ignore[assignment]


class LightRAGDocumentLoader(DocumentLoader):
    def __init__(self, data_source: DataSource):
        """Generic document loader that loads documents from a location."""
        super().__init__(data_source=data_source)

    def load_documents(
        self, **kwargs
    ) -> Iterator[tuple[Document, list[Document] | None]]:
        files = [
            str(file)
            for file in Path(self.data_source.location).rglob("*")
            if file.is_file()
        ]

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
                    "doc_location": str(doc_location),
                    "last_updated": datetime.now().isoformat(),
                    "tags": self.data_source.tags,
                },
            )
            yield parent_doc, None


class LightRAGKnowledgebase(GraphKnowledgebase):
    init_lock = asyncio.Lock()
    """ Important we only initialize one KB at a time because LightRAG uses env vars for setting up the DB connection """

    def __init__(
        self,
        working_dir: PathLike | str,
        llm_api_key: str,  # TODO: perhaps we can pass an LLM in instead
        llm_api_url: str,
        llm_api_model: str,
        aiware_key: str,
        db_url: str,
        db_port: int,
        db_user: str,
        db_password: str,
        # embedding_model: Embeddings,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ):
        """Initialize the LightRAG knowledge base.

        Args:
            working_dir (PathLike | str): Directory to store temporary LightRAG working files.
            collection (str): Name of the collection to use for the knowledge base, this separates the knowledge bases in the same database.
            llm_api_key (str): API key for an OpenAI-compatbile LLM service (e.g. the Veritone LiteLLM Gateway)
            llm_api_url (str): URL for the LLM service.
            llm_api_model (str): Model to use for the LLM service. This is a model name for the LLM service, e.g. "azure/gpt-4o-mini".
            db_url (str): URL for the PostgreSQL database.
            db_port (int): Port for the PostgreSQL database.
            db_user (str): Username for the PostgreSQL database.
            db_password (str): Password for the PostgreSQL database.

        Example:

            lrkb = LightRAGKnowledgebase(
                name="faux_211_289_287",
                collection="faux_211_289_287",
                working_dir="./lightrag_tmp",
                llm_api_key=os.getenv("LLM_GATEWAY_API_KEY", ""),
                llm_api_url=os.getenv("LLM_GATEWAY_API_URL", ""),
                llm_api_model="azure/gpt-4o-mini",
                db_url=os.getenv("POSTGRES_HOST", ""),
                db_port=int(os.getenv("POSTGRES_PORT", 5432)),
                db_user=os.getenv("POSTGRES_USER", ""),
                db_password=os.getenv("POSTGRES_PASSWORD", ""),
            )
        """
        super().__init__(**kwargs)
        self.initialized = False

        # Use workspaces in future?
        # This is a critical section as we have to rely on the LightRAG class to store
        # the env vars, otherwise we can't have multiple LightRAG objects easily
        self.db_url = db_url
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.database = self.metadata.collection
        self.workspace = self.metadata.collection
        self.llm_api_model = llm_api_model
        self.llm_api_key = llm_api_key
        self.llm_api_url = llm_api_url
        self.aiware_key = aiware_key

        self._set_env_vars()
        self.rag = LightRAG(
            working_dir=str(working_dir),
            llm_model_func=self.llm_model_func,
            # llm_model_func=None,
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=5000,
                func=lambda texts: hf_embed(
                    texts,
                    tokenizer=AutoTokenizer.from_pretrained("thenlper/gte-base"),
                    embed_model=AutoModel.from_pretrained("thenlper/gte-base"),
                ),
            ),
            kv_storage="PGKVStorage",
            doc_status_storage="PGDocStatusStorage",
            graph_storage="PGGraphStorage",
            vector_storage="PGVectorStorage",
            auto_manage_storages_states=False,
        )

    async def llm_model_func(
        self,
        prompt,
        system_prompt=None,
        history_messages=[],
        keyword_extraction=False,
        **kwargs,
    ) -> str:
        return await openai_complete_if_cache(
            self.llm_api_model,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=self.llm_api_key,
            base_url=self.llm_api_url,
            extra_headers={"x-aiware-api-token": self.aiware_key},
            **kwargs,
        )

    def _set_env_vars(self):
        current_db_name.set(self.database) # pyright: ignore[reportArgumentType]
        os.environ["POSTGRES_WORKSPACE"] = self.workspace # pyright: ignore[reportArgumentType]
        os.environ["POSTGRES_DATABASE"] = self.database # pyright: ignore[reportArgumentType]
        os.environ["POSTGRES_HOST"] = self.db_url
        os.environ["POSTGRES_PORT"] = str(self.db_port)
        os.environ["POSTGRES_USER"] = self.db_user
        os.environ["POSTGRES_PASSWORD"] = self.db_password

    async def _initialize(self):
        if not self.initialized:
            async with LightRAGKnowledgebase.init_lock:
                # Unfortunately LightRAG uses env vars to set up the DB connection
                # It is really critical here that LightRAG.initialize_storages actually stores the
                # env vars in local members so we can have multiple LightRAG objects with different settings
                self._set_env_vars()
                try:
                    await self.rag.initialize_storages()
                except asyncpg.exceptions.InvalidCatalogNameError:
                    # unfortunately we have to break the abstraction here if the DB does not exist
                    # perhaps we can do a PR
                    conn = await asyncpg.connect(
                        user=self.db_user,
                        password=self.db_password,
                        host=self.db_url,
                        port=self.db_port,
                        database="postgres",  # must connect to an existing DB to create a new one
                    )
                    await conn.execute(f"CREATE DATABASE {self.database}")
                    await conn.close()
                    conn = await asyncpg.connect(
                        user=self.db_user,
                        password=self.db_password,
                        host=self.db_url,
                        port=self.db_port,
                        database=self.database,
                    )
                    await conn.execute("CREATE EXTENSION vector;")
                    await conn.execute("CREATE EXTENSION age;")
                    await conn.close()
                    await self.rag.initialize_storages()
                await initialize_pipeline_status()
                self.initialized = True

    async def asearch(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ) -> tuple[str, list[Document]]:
        await self._initialize()

        mode = "hybrid"
        result = await self.rag.aquery(
            query, param=QueryParam(mode=mode, top_k=limit, only_need_prompt=True)
        )
        return str(result), []

    def graph_retrieve(
        self,
        query: str | dict[str, str],
        limit: int,
        **kwargs,
    ) -> tuple[str, SubGraph]:
        """Retrieve a subgraph from the knowledge base graph based on a natural language query."""
        loop = always_get_an_event_loop()
        loop.run_until_complete(self._initialize())
        return loop.run_until_complete(self.agraph_retrieve(query, limit, **kwargs))

    async def agraph_retrieve(
        self,
        query: str | dict[str, str],
        limit: int,
        **kwargs,
    ) -> tuple[str, SubGraph]:
        """Retrieve a subgraph from the knowledge base graph based on a natural language query."""
        await self._initialize()

        # TODO: omg
        use_model_func = self.llm_model_func
        use_model_func = partial(use_model_func, _priority=5)
        mode = "hybrid"
        query_param = QueryParam(mode=mode, top_k=limit, only_need_prompt=True)
        from dataclasses import asdict

        global_config = asdict(self.rag)
        hashing_kv = self.rag.llm_response_cache

        # TODO: we should pull this out from LightRAG and run our own keyword extraction with LangChain LLMs
        if isinstance(query, str):
            hl_keywords, ll_keywords = await operate.get_keywords_from_query(
                query, query_param, global_config, hashing_kv
            )
            hl_keywords_str = ", ".join(hl_keywords) if hl_keywords else ""
            ll_keywords_str = ", ".join(ll_keywords) if ll_keywords else ""
        else:
            # If query is a dict, we assume it contains keywords for high-level and low-level queries
            hl_keywords_str = query.get("high_level_keywords")
            ll_keywords_str = query.get("low_level_keywords")

        log.info(f"High-level keywords: {hl_keywords_str}")
        log.info(f"Low-level  keywords: {ll_keywords_str}")

        ll_data = None
        hl_data = None
        if ll_keywords_str:
            ll_data = await operate._get_node_data(
                ll_keywords_str,
                self.rag.chunk_entity_relation_graph,
                self.rag.entities_vdb,
                self.rag.text_chunks,
                query_param, # pyright: ignore[reportCallIssue]
            )

        if hl_keywords_str:
            hl_data = await operate._get_edge_data(
                hl_keywords_str,
                self.rag.chunk_entity_relation_graph,
                self.rag.relationships_vdb,
                self.rag.text_chunks,
                query_param, # pyright: ignore[reportCallIssue]
            )

        if ll_data and hl_data:
            (
                ll_entities_context,
                ll_relations_context,
                ll_text_units_context,
            ) = ll_data
            (
                hl_entities_context,
                hl_relations_context,
                hl_text_units_context,
            ) = hl_data

            # Combine and deduplicate the entities, relationships, and sources
            entities_context = operate.process_combine_contexts( # pyright: ignore[reportAttributeAccessIssue]
                hl_entities_context, ll_entities_context
            )
            relations_context = operate.process_combine_contexts( # pyright: ignore[reportAttributeAccessIssue]
                hl_relations_context, ll_relations_context
            )
            text_units_context = operate.process_combine_contexts( # pyright: ignore[reportAttributeAccessIssue]
                hl_text_units_context, ll_text_units_context
            )
        elif ll_data:
            entities_context, relations_context, text_units_context = ll_data
        elif hl_data:
            entities_context, relations_context, text_units_context = hl_data
        else:
            log.error("No data found for the query." + str(query))
            return "", SubGraph()

        # Example for entities_context entry
        # x = {
        #     "id": "1",
        #     "entity": "Jane Doe",
        #     "type": "person",
        #     "description": "Jane Doe is a victim in the incident described, experiencing a traumatic event involving Suspect 1 and Suspect 2.<SEP>Jane Doe is a victim involved in a robbery and sexual assault incident, characterized by her relationship with John Doe and her college studies.",
        #     "rank": 7,
        #     "created_at": "UNKNOWN",
        #     "file_path": "Faux 211 289 287.docx",
        # }
        nodes = [
            GraphNode(
                name=entity["entity"],
                source_chunk=None,  # TODO
                metadata={
                    "entity_type": entity["type"],
                    "description": entity["description"],
                    "rank": entity["rank"],
                    "created_at": entity.get("created_at", "UNKNOWN"),
                    "file_path": entity.get("file_path", ""),
                },
            )
            for entity in entities_context
            if isinstance(entity, dict) and "entity" in entity
        ]

        # Example for relations_context entry
        # y = {
        #     "id": "1",
        #     "entity1": "Jane Doe",
        #     "entity2": "Suspect 1",
        #     "description": "Jane Doe is attacked by Suspect 1 during the assault.<SEP>Suspect 1 was involved in the sexual assault against Jane Doe, contributing to the traumatic event she experienced.",
        #     "keywords": "crime involvement, perpetrator-victim<SEP>victim-perpetrator, assault",
        #     "weight": 20.0,
        #     "rank": 9,
        #     "created_at": "2025-05-13 09:08:28",
        #     "file_path": "Faux 211 289 287.docx",
        # }
        edges = [
            GraphEdge(
                source_node=relation["entity1"],
                target_node=relation["entity2"],
                source_chunk=None,  # TODO
                metadata={
                    "description": relation["description"],
                    "keywords": relation["keywords"],
                    "weight": relation["weight"],
                    "rank": relation["rank"],
                    "created_at": relation.get("created_at", "UNKNOWN"),
                    "file_path": relation.get("file_path", ""),
                },
            )
            for relation in relations_context
            if isinstance(relation, dict)
            and "entity1" in relation
            and "entity2" in relation
        ]

        # Example for text_units_context entry
        # z = {
        #        "id": "1",
        #        "content": "On 4/1/2025, at approximately 0100 hours...",
        #        "file_path": "Faux 211 289 287.docx",
        #    },
        documents = [
            Document(id=tu["file_path"], page_content=tu["content"])
            for tu in text_units_context
            if isinstance(tu, dict) and "content" in tu and "file_path" in tu
        ]

        ret = """
             Results from the retrieval of the knowledge graph, represented as entities and relationships and relevant document chunks.
             When handling relationships with timestamps:
                1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge\n
                2. When encountering conflicting relationships, consider both the semantic content and the timestamp\n
                3. Don't automatically prefer the most recently created relationships - use judgment based on the context\n
                4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps\n
                \n
            """
        entities_str = json.dumps(entities_context, ensure_ascii=False)
        relations_str = json.dumps(relations_context, ensure_ascii=False)
        text_units_str = json.dumps(text_units_context, ensure_ascii=False)

        ret += f"""-----Entities(KG)-----
            ```json
            {entities_str}
            ```

            -----Relationships(KG)-----

            ```json
            {relations_str}
            ```

            -----Document Chunks(DC)-----

            ```json
            {text_units_str}
            ```

            """

        return ret, SubGraph(
            nodes=nodes,
            edges=edges,
            chunks=documents,
        )

    def get_documents(
        self, filter: KnowledgeFilter | None = None
    ) -> Iterator[Document]:
        """Get all documents from the knowledge base.
        Args:
            filter (KnowledgeFilter | None): Optional filter to apply to the documents.
        Returns:
            Iterator[Document]: An iterator over the documents in the knowledge base.
        """
        loop = always_get_an_event_loop()
        loop.run_until_complete(self._initialize())

        async def consume():
            return [i async for i in self.aget_documents(filter=filter)]

        for doc in loop.run_until_complete(consume()):
            yield doc

    async def aget_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Get all documents from the knowledge base.
        Args:
            filter (KnowledgeFilter | None): Optional filter to apply to the documents.
        Returns:
            Iterator[Document]: An iterator over the documents in the knowledge base.
        """
        await self._initialize()
        docs = await self.rag.get_docs_by_status(DocStatus.PROCESSED)
        for did, doc in docs.items():
            doc_name = Path(doc.file_path).name
            # doc_location = #Path(doc.file_path).relative_to(self.data_source.location).parent

            yield Document(
                id=did,
                page_content="", # TODO
                metadata={
                    "source": did,
                    "summary": doc.content_summary,
                    "doc_name": doc_name,
                    "last_updated": doc.updated_at,
                    # "data_source":
                    # "status": doc.status,
                },
            )

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
            kwargs (Any): Additional keyword arguments for tool configuration, typically num_results exists.
            name_suffix: str | None = None,
            runnable_config_filter_prefix: str | None = None,
        Returns:
            list[BaseTool]: List of tools for the knowledge base.
        """
        tools = []
        if search_tools:
            tools.append(
                LightRAGQuery(
                    knowledgebase=self,
                    name_suffix=f"_{self.metadata.collection if name_suffix is None else name_suffix}",
                    num_results=kwargs.get("num_results", 10),
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

    def get_graph(self):
        loop = always_get_an_event_loop()
        loop.run_until_complete(self._initialize())
        return loop.run_until_complete(self._export_graph())

    async def aget_graph(self):
        await self._initialize()
        return await self._export_graph()

    def close(self):
        """Finalize the storages when the object is deleted."""
        loop = always_get_an_event_loop()
        self._set_env_vars()
        loop.run_until_complete(self.rag.finalize_storages())

    async def aclose(self):
        """Finalize the storages when the object is deleted."""
        self._set_env_vars()
        await self.rag.finalize_storages()

    async def aget_edges(self) -> list[GraphEdge]:
        """Get all edges/relations from the knowledge base."""
        return await self._get_edges()

    def get_edges(self) -> list[GraphEdge]:
        """Get all relations from the knowledge base."""
        loop = always_get_an_event_loop()
        loop.run_until_complete(self._initialize())
        return loop.run_until_complete(self._get_edges())

    async def _get_edges(self) -> list[GraphEdge]:
        """Get all edges from the graph.
        This is a workaround to get all edges from the graph, as LightRAG does not provide a direct method for this.
        Likely only works with PostgreSQL and AGE extension.
        """
        db = cast(PGGraphStorage, self.rag.chunk_entity_relation_graph)
        query = (
            """SELECT * FROM cypher('%s', $$
                      MATCH (source)-[e]->(target)
                      RETURN source.entity_id AS source_entity_id, target.entity_id AS target_entity_id, e $$)
                    AS (source_entity_id text, target_entity_id text, e agtype);"""
            % db.graph_name
        )
        results = await db._query(query)
        return [
            GraphEdge(
                source_node=result["source_entity_id"],
                target_node=result["target_entity_id"],
                source_chunk=result.get("e", {})
                .get("properties", {})
                .get("source_id", None),
                metadata=result.get("e", {}).get("properties", {}),
            )
            for result in results
        ]

    async def aget_nodes(self) -> list[GraphNode]:
        """Get all nodes/entities from the knowledge base."""
        return await self._get_nodes()

    def get_nodes(self) -> list[GraphNode]:
        """Get all nodes/entities from the knowledge base."""
        loop = always_get_an_event_loop()
        loop.run_until_complete(self._initialize())
        return loop.run_until_complete(self._get_nodes())

    async def _get_nodes(self) -> List[GraphNode]:
        chunk_entity_relation_graph = self.rag.chunk_entity_relation_graph
        nodes: list[GraphNode] = []
        all_entities = await chunk_entity_relation_graph.get_all_labels()
        for entity_name in all_entities:
            # Get entity information from graph
            node_data = await chunk_entity_relation_graph.get_node(entity_name)
            source_id = node_data.get("source_id") if node_data else None
            nodes.append(
                GraphNode(
                    name=entity_name,
                    source_chunk=source_id,
                    metadata=node_data or {},
                )
            )
        return nodes

    async def _export_graph(self):
        return Graph(
            nodes=await self._get_nodes(),
            edges=await self._get_edges(),
        )


class RWLightRAGKnowledgebase(LightRAGKnowledgebase, RWGraphKnowledgebase):
    def __init__(
        self, data_sources: list[DataSourceOrLoader] | None = None, **kwargs
    ):
        super().__init__(data_sources=data_sources, **kwargs)

    def index(self, data_source: Optional[DataSourceOrLoader] = None):
        """Do an index run on either a provides data source or data sources defined in its config.

        Args:
            data_source (DataSource): Data source to index. If None, will use the data sources defined in the config.
            If a DocumentLoader is provided, it will be used to load documents from the data source, otherwise the a generic data loader will be used.
        """
        loop = always_get_an_event_loop()
        data_sources = [data_source] if data_source else self.data_sources
        for ds in data_sources:
            loop.run_until_complete(self._aindex(ds))

    async def _aindex(self, data_source: DataSourceOrLoader):
        await self._initialize()

        loader, data_source = self._acquire_loader(data_source, LightRAGDocumentLoader)
        log.info(f"Indexing {loader.data_source.name} ({loader.data_source.location})")
        docs = loader.load_documents()

        # we don't chunk into children, LightRAG does that for us
        for parent_doc, _ in docs:
            # retrieve existing document and compare
            parent_doc_id = parent_doc.metadata["source"]
            await self.rag.ainsert(
                parent_doc.page_content,
                ids=parent_doc_id,
                file_paths=parent_doc.metadata.get("doc_name", parent_doc.metadata.get("source", "unknown")),
            )


async def main():
    import os

    lrkb = LightRAGKnowledgebase(
        # name="rtca_faux187",
        # collection="rtca_faux187",
        name="veritone_peopleops_us_graph",
        collection="veritone_people_us",
        working_dir="./lightrag_tmp",
        llm_api_key=os.getenv("LLM_GATEWAY_API_KEY", ""),
        llm_api_url=os.getenv("LLM_GATEWAY_API_URL", ""),
        llm_api_model="azure/gpt-4o-mini",
        aiware_key=os.getenv("LLM_GATEWAY_AIWARE_KEY", ""),
        db_url=os.getenv("POSTGRES_HOST", ""),
        db_port=int(os.getenv("POSTGRES_PORT", 5432)),
        db_user=os.getenv("POSTGRES_USER", ""),
        db_password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    # async for doc in lrkb.aget_documents():
    #    print(doc)
    # retrieved = await lrkb.aretrieve(
    #   query="Who is the victim?",
    #   limit=5,
    # )
    # print(retrieved)
    # print("Labels:")
    # print(await lrkb.rag.get_graph_labels())

    # export graph
    # ret = await lrkb.get_graph(include_vector_data=False)
    # ret = await lrkb.aget_graph()
    # print(ret)
    retrieved = await lrkb.agraph_retrieve(
        query="Get everything related to pet insurance",
        limit=2,
    )
    print(retrieved)
    await lrkb.aclose()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
