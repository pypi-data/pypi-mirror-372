import logging
from os import PathLike
from typing import Any, AsyncGenerator, Iterator, Optional, List, Dict, cast
from collections.abc import Sequence

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from veri_agents_knowledgebase.types import Document, DocumentChunks, DocumentReference

log = logging.getLogger(__name__)


class KnowledgeFilter(BaseModel):
    """Filter for knowledge base queries.

    The filter is applied as follows:
    OR(pre_tags_any_of) AND
    AND(pre_tags_all_of) AND
    AND(tags_all_of) AND
    OR(tags_any_of)  AND
    OR(docs)

    tags_* can typically be controlled by an agent, while pre_tags_* are usually set by the system to avoid the agent
    accessing documents it should not have access to.
    """

    docs: list[str] | str | None = None
    """ List of document IDs or single document ID to filter by. """

    pre_tags_any_of: list[str] | str | None = None
    """ List of tags to filter by, if any of the provided tags matches, a document is selected.
        This is used to limit the search space an agent has access to in subsequent filters.
        For example you can use this to limit the search space to a specific project in which the
        agent is then allowed to apply additional tags.

        Those filters are also transparent to the agent, meaning that the agent does not know about them while
        if the user sets the tags_any_of or tags_all_of, the agent will be made aware of this choice.
    """

    pre_tags_all_of: list[str] | str | None = None
    """ List of tags to filter by, if all of the provided tags match, a document is selected.
        This is used to limit the search space an agent has access to in subsequent filters.
        For example you can use this to limit the search space to a specific project in which the
        agent is then allowed to apply additional tags.

        Those filters are also transparent to the agent, meaning that the agent does not know about them while
        if the user sets the tags_any_of or tags_all_of, the agent will be made aware of this choice.
    """

    tags_any_of: list[str] | str | None = None
    """ List of tags to filter by, if any of the provided tags matches, a document is selected. 
        This can usually also be set by an agent.
    """

    tags_all_of: list[str] | str | None = None
    """ List of tags to filter by, if all of the provided tags match, a document is selected. 
        This can usually also be set by an agent.
    """

    @property
    def docs_list(self) -> list[str] | None:
        if self.docs is None:
            return None
        return self.docs if isinstance(self.docs, list) else [self.docs]

    def __repr__(self):
        return f"KnowledgeFilter(docs={self.docs}, tags_any_of={self.tags_any_of}, tags_all_of={self.tags_all_of})"

    def __str__(self):
        return f"KnowledgeFilter(docs={self.docs}, tags_any_of={self.tags_any_of}, tags_all_of={self.tags_all_of})"


def and_filters(filter1: KnowledgeFilter | None, filter2: KnowledgeFilter | None):
    if filter1 is None:
        return filter2
    elif filter2 is None:
        return filter1
    else:
        # docs
        if filter1.docs is None:
            docs = filter2.docs
        elif filter2.docs is None:
            docs = filter1.docs
        else:
            # intersection
            docs1 = (
                filter1.docs
                if isinstance(filter1.docs, Sequence)
                and not isinstance(filter1.docs, str)
                else [cast(str, filter1.docs)]
            )
            docs2 = (
                filter2.docs
                if isinstance(filter2.docs, Sequence)
                and not isinstance(filter2.docs, str)
                else [cast(str, filter2.docs)]
            )

            docs = list(set(docs1) & set(docs2))

        # tags_any_of
        if filter1.tags_any_of is None:
            tags_any_of = filter2.tags_any_of
        elif filter2.tags_any_of is None:
            tags_any_of = filter1.tags_any_of
        else:
            # union
            tags_any_of1 = (
                filter1.tags_any_of
                if isinstance(filter1.tags_any_of, Sequence)
                and not isinstance(filter1.tags_any_of, str)
                else [cast(str, filter1.tags_any_of)]
            )
            tags_any_of2 = (
                filter2.tags_any_of
                if isinstance(filter2.tags_any_of, Sequence)
                and not isinstance(filter2.tags_any_of, str)
                else [cast(str, filter2.tags_any_of)]
            )

            tags_any_of = list(set(tags_any_of1) | set(tags_any_of2))

        # tags_all_of
        if filter1.tags_all_of is None:
            tags_all_of = filter2.tags_all_of
        elif filter2.tags_all_of is None:
            tags_all_of = filter1.tags_all_of
        else:
            # union
            tags_all_of1 = (
                filter1.tags_all_of
                if isinstance(filter1.tags_all_of, Sequence)
                and not isinstance(filter1.tags_all_of, str)
                else [cast(str, filter1.tags_all_of)]
            )
            tags_all_of2 = (
                filter2.tags_all_of
                if isinstance(filter2.tags_all_of, Sequence)
                and not isinstance(filter2.tags_all_of, str)
                else [cast(str, filter2.tags_all_of)]
            )

            tags_all_of = list(set(tags_all_of1) | set(tags_all_of2))

        # pre_tags_any_of
        if filter1.pre_tags_any_of is None:
            pre_tags_any_of = filter2.pre_tags_any_of
        elif filter2.pre_tags_any_of is None:
            pre_tags_any_of = filter1.pre_tags_any_of
        else:
            # union
            pre_tags_any_of1 = (
                filter1.pre_tags_any_of
                if isinstance(filter1.pre_tags_any_of, Sequence)
                and not isinstance(filter1.pre_tags_any_of, str)
                else [cast(str, filter1.pre_tags_any_of)]
            )
            pre_tags_any_of2 = (
                filter2.pre_tags_any_of
                if isinstance(filter2.pre_tags_any_of, Sequence)
                and not isinstance(filter2.pre_tags_any_of, str)
                else [cast(str, filter2.pre_tags_any_of)]
            )
            pre_tags_any_of = list(set(pre_tags_any_of1) | set(pre_tags_any_of2))

        # pre_tags_all_of
        if filter1.pre_tags_all_of is None:
            pre_tags_all_of = filter2.pre_tags_all_of
        elif filter2.pre_tags_all_of is None:
            pre_tags_all_of = filter1.pre_tags_all_of
        else:
            # union
            pre_tags_all_of1 = (
                filter1.pre_tags_all_of
                if isinstance(filter1.pre_tags_all_of, Sequence)
                and not isinstance(filter1.pre_tags_all_of, str)
                else [cast(str, filter1.pre_tags_all_of)]
            )
            pre_tags_all_of2 = (
                filter2.pre_tags_all_of
                if isinstance(filter2.pre_tags_all_of, Sequence)
                and not isinstance(filter2.pre_tags_all_of, str)
                else [cast(str, filter2.pre_tags_all_of)]
            )
            pre_tags_all_of = list(set(pre_tags_all_of1) | set(pre_tags_all_of2))

        return KnowledgeFilter(
            docs=docs,
            tags_any_of=tags_any_of,
            tags_all_of=tags_all_of,
            pre_tags_any_of=pre_tags_any_of,
            pre_tags_all_of=pre_tags_all_of,
        )


class DataSource(BaseModel):
    """Data source for a knowledge base."""

    location: PathLike | str = Field(
        description="Location of the data source, e.g. a file path or URL."
    )
    name: str = Field(
        description="Name of the data source. Can be used for filtering in the knowledgebase and important that document names are unique"
    )
    tags: list[str] = Field(
        default=[],
        description="Tags applied to all documents and chunks of the source, e.g. 'finance'.",
    )
    incremental: bool = Field(
        default=False,
        description="Whether to do incremental indexing of the data source.",
    )

    def __repr__(self) -> str:
        return f"DataSource(location={self.location}, name={self.name}, tags={self.tags}, incremental={self.incremental})"

    def __str__(self) -> str:
        return f"DataSource(location={self.location}, name={self.name}, tags={self.tags}, incremental={self.incremental})"


class DocumentLoader:
    """Loads data from a data source and returns documents."""

    def __init__(self, data_source: DataSource):
        self.data_source = data_source

    def load_documents(
        self, **kwargs
    ) -> Iterator[tuple[Document, list[Document] | None]]:
        """Parse documents from a data source.

        Args:
            kwargs: Additional arguments to pass to the loader.

        Returns:
            Iterator[tuple[Document, Document | None]]: An iterator of tuples containing the document and optionally a list of child documents.
        """
        raise NotImplementedError


DataSourceOrLoader = DataSource | DocumentLoader
""" Type alias for a data source or a document loader. This allows functions to accept either a DataSource or a DocumentLoader, providing flexibility in how data is loaded into the knowledge base."""

class KnowledgebaseMetadata(BaseModel):
    """Metadata for knowledgebases.
        This is metadata that can be serialized to an API to provide information about the knowledgebase.
    """

    name: str
    """ Name of the knowledgebase, used for identification and retrieval."""

    description: str | None = None
    """ Description of the knowledgebase, used by agents to decide which knowlegebase to query. """

    tags: dict[str, str] = {}
    """ Tags applied to the knowledgebase, e.g. 'finance', 'legal'. Used for filtering and retrieval.
        Keys are tag names, values are descriptions of the tags used for the autotagger. """

    collection: str | None = None
    """ Collection name for the knowledgebase, used for grouping and retrieval. """

    doc_summarize: bool = False
    """ Summarize documents in the knowledgebase. """

    doc_autotag: bool = False
    """ Autotag when indexing. """

    class Config:
        extra = "ignore"


class Knowledgebase:
    def __init__(self, **kwargs):
        self.metadata = KnowledgebaseMetadata.model_validate(kwargs)

    @property
    def tags(self):
        """Get the tags for the workflow."""
        return self.metadata.tags

    @property
    def name(self):
        """Get the name of the workflow."""
        return self.metadata.name

    @property
    def description(self):
        """Get the description of the workflow."""
        return self.metadata.description

    def search(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[DocumentChunks | Document]:
        """ Search the knowledge base.
        
        Args:
            query (str): The query to search for documents.
            limit (int): The maximum number of documents to retrieve.
            filter (KnowledgeFilter | None): Optional filter to apply to the retrieval.

        Returns:
            Iterator[DocumentChunks]: the retrieved documents' chunks.
        """
        raise NotImplementedError

    def asearch(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[DocumentChunks | Document, None]:
        """Asynchronously search the knowledge base.
        
        Args:
            query (str): The query to search for documents.
            limit (int): The maximum number of documents to retrieve.
            filter (KnowledgeFilter | None): Optional filter to apply to the retrieval.
        Returns:
            Iterator[DocumentChunks]: the retrieved documents' chunks.
        """
        raise NotImplementedError

    def list_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[DocumentReference]:
        """Get all documents from the knowledge base.
        
        Args:
            filter (KnowledgeFilter | None): Optional filter to apply to the documents.
        
        Returns:
            Iterator[DocumentReference]: An iterator over the documents in the knowledge base.
        """
        raise NotImplementedError

    def alist_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[DocumentReference, None]:
        """Asynchronously get all documents from the knowledge base.
        
        Args:
            filter (KnowledgeFilter | None): Optional filter to apply to the documents.

        Returns:
            AsyncGenerator[DocumentReference, None]: An asynchronous generator yielding documents from the knowledge base.
        """
        raise NotImplementedError

    def get_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[Document]:
        """Get all documents from the knowledge base.
        
        Args:
            filter (KnowledgeFilter | None): Optional filter to apply to the documents.
        
        Returns:
            Iterator[Document]: An iterator over the documents in the knowledge base.
        """
        raise NotImplementedError

    def aget_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Asynchronously get all documents from the knowledge base.
        
        Args:
            filter (KnowledgeFilter | None): Optional filter to apply to the documents.

        Returns:
            AsyncGenerator[Document, None]: An asynchronous generator yielding documents from the knowledge base.
        """
        raise NotImplementedError

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
            retrieve_tools (bool): Whether to include tools for retrieving documents.
            list_tools (bool): Whether to include tools for listing documents.
            write_tools (bool): Whether to include tools for writing documents.
            name_suffix (str | None): Optional suffix to append to the tool names.
            runnable_config_filter_prefix (str | None): Optional prefix for the runnable config filter.
            kwargs (Any): Additional keyword arguments for tool configuration, typically num_results exists.
        Returns:
            list[BaseTool]: List of tools for the knowledge base.
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"Knowledgebase(name={self.name}, description={self.description}, tags={self.tags})"

    def __str__(self) -> str:
        return f"Knowledgebase {self.name} ({self.description})"


class RWKnowledgebase(Knowledgebase):
    def __init__(self, data_sources: list[DataSourceOrLoader] | None = None, **kwargs):
        super().__init__(**kwargs)
        self.data_sources: list[DataSourceOrLoader] = data_sources or []

    def _acquire_loader(
        self, data_source: DataSourceOrLoader, doc_loader_cls: type[DocumentLoader]
    ) -> tuple[DocumentLoader, DataSource]:
        """Acquire a document loader for the given data source or return if a loader is already provides."""
        if isinstance(data_source, DocumentLoader):
            return data_source, data_source.data_source
        elif isinstance(data_source, DataSource):
            return doc_loader_cls(data_source), data_source

    def index(self, data_source: Optional[DataSourceOrLoader] = None):
        """Do an index run on either a provides data source or the data sources passed in the constructor.

        Args:
            data_source (DataSourceOrLoader): Data source to index. If None, will use the data sources passed in through the constructor.
            If a DocumentLoader is provided, it will be used to load documents from the data source, otherwise the a generic data loader will be used.
        """
        data_sources = [data_source] if data_source else self.data_sources
        for ds in data_sources:
            self._index(ds)

    async def aindex(self, data_source: Optional[DataSourceOrLoader] = None):
        """Do an index run on either a provides data source or the data sources passed in the constructor.

        Args:
            data_source (DataSourceOrLoader): Data source to index. If None, will use the data sources passed in through the constructor.
            If a DocumentLoader is provided, it will be used to load documents from the data source, otherwise the a generic data loader will be used.
        """
        data_sources = [data_source] if data_source else self.data_sources
        for ds in data_sources:
            await self._aindex(ds)

    async def _aindex(self, data_source: DataSourceOrLoader):
        """Index a single data source asynchronously."""
        raise NotImplementedError(
            "Asynchronous indexing is not implemented for this knowledge base."
        )

    def _index(self, data_source: DataSourceOrLoader):
        """Index a single data source synchronously."""
        raise NotImplementedError(
            "Synchronous indexing is not implemented for this knowledge base."
        )

    def set_tags(
        self,
        doc_id: str,
        tags: list[str],
    ):
        """Add tags to a document.

        Args:
            doc_id (str): ID of the document to tag.
            tags (list[str]): List of tags to add to the document.
        """
        raise NotImplementedError


class GraphNode(BaseModel):
    """Node representation in a graph, typically an entity in a knowledge base."""

    name: str = Field(
        description="Name of the node, typically an entity in the knowledge base."
    )
    source_chunk: str | None = Field(
        description="From which this node was created, e.g. a chunk/document ID."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata associated with the node, e.g. tags, description, etc.",
    )


class GraphEdge(BaseModel):
    """Edge representation in a graph, typically a relation between entities."""

    source_node: str = Field(description="Source node ID of the edge.")
    target_node: str = Field(description="Target node ID of the edge.")
    source_chunk: str | None = Field(
        description="From which this edge was created, e.g. a chunk/document ID."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata associated with the edge, e.g. confidence score, description, etc.",
    )


class Graph(BaseModel):
    """Graph representation of a knowledge base."""

    nodes: List[GraphNode] = Field(
        default_factory=list, description="List of nodes in the graph."
    )
    edges: List[GraphEdge] = Field(
        default_factory=list, description="List of edges in the graph."
    )

    def find_node(self, node_name: str) -> GraphNode | None:
        """Find a node by its name."""
        for node in self.nodes:
            if node.name == node_name:
                return node
        return None

    def is_empty(self) -> bool:
        """Check if the graph is empty."""
        return len(self.nodes) == 0 and len(self.edges) == 0


class SubGraph(BaseModel):
    """Subset of a graph, typically result of a retrieval process."""

    nodes: List[GraphNode] = Field(
        default_factory=list, description="List of nodes in the subset."
    )
    edges: List[GraphEdge] = Field(
        default_factory=list, description="List of edges in the subset."
    )
    chunks: List[Document] = Field(
        default_factory=list,
        description="List of chunks that are part of the subset.",
    )

    def find_node(self, node_name: str) -> GraphNode | None:
        """Find a node by its name."""
        for node in self.nodes:
            if node.name == node_name:
                return node
        return None


class GraphKnowledgebase(Knowledgebase):
    """Knowledgebase that support graph queries."""

    async def aget_nodes(self) -> list[GraphNode]:
        """Get all nodes/entities from the knowledge base."""
        raise NotImplementedError

    def get_nodes(self) -> list[GraphNode]:
        """Get all nodes/entities from the knowledge base."""
        raise NotImplementedError

    async def aget_edges(self) -> list[GraphEdge]:
        """Get all edges/relations from the knowledge base."""
        raise NotImplementedError

    def get_edges(self) -> list[GraphEdge]:
        """Get all edges/relations from the knowledge base."""
        raise NotImplementedError

    def get_graph(self) -> Graph:
        """Get the graph representation of the knowledge base."""
        raise NotImplementedError

    async def aget_graph(self) -> Graph:
        """Get the graph representation of the knowledge base asynchronously."""
        raise NotImplementedError

    def graph_retrieve(
        self,
        query: str | dict[str, str],
        limit: int,
        **kwargs,
    ) -> tuple[str, SubGraph]:
        """Retrieve a subgraph from the knowledge base graph based on a natural language query.

        Args:
            query (str | dict[str, str]): Natural language query or structured query.
                        For example LightRAG queries can be a dict of {"high_level_keywords": "keyword1, keyword2", "low_level_keywords": "keyword3, keyword4"}.
            limit (int): Maximum number of nodes to retrieve.
            **kwargs: Additional arguments for the retrieval process.
        Returns:
            tuple[str, SubGraph]: A tuple containing a prompt for an LLM and the retrieved subgraph.
        """
        raise NotImplementedError

    async def agraph_retrieve(
        self,
        query: str | dict[str, str],
        limit: int,
        **kwargs,
    ) -> tuple[str, SubGraph]:
        """Retrieve a subgraph from the knowledge base graph based on a natural language query.

        Args:
            query (str | dict[str, str]): Natural language query or structured query.
                        For example LightRAG queries can be a dict of {"high_level_keywords": "keyword1, keyword2", "low_level_keywords": "keyword3, keyword4"}.
            limit (int): Maximum number of nodes to retrieve.
            **kwargs: Additional arguments for the retrieval process.
        Returns:
            tuple[str, SubGraph]: A tuple containing a prompt for an LLM and the retrieved subgraph.
        """
        raise NotImplementedError


class RWGraphKnowledgebase(GraphKnowledgebase, RWKnowledgebase):
    """Read-write graph knowledge base that supports graph mutations."""

    def add_node(self, node: GraphNode):
        """Add a node to the knowledge base graph."""
        raise NotImplementedError

    async def aadd_node(self, node: GraphNode):
        """Add a node to the knowledge base graph asynchronously."""
        raise NotImplementedError

    def add_edge(self, edge: GraphEdge):
        """Add an edge to the knowledge base graph."""
        raise NotImplementedError

    async def aadd_edge(self, edge: GraphEdge):
        """Add an edge to the knowledge base graph asynchronously."""
        raise NotImplementedError
