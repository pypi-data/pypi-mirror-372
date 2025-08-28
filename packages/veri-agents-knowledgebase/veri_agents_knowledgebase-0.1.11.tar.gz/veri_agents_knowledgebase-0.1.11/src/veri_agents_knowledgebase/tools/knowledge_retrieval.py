import logging
from typing import Callable, Optional, Tuple, Unpack

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel, Field
from veri_agents_knowledgebase.knowledgebase import Knowledgebase, KnowledgeFilter
from veri_agents_knowledgebase.types import Document, DocumentChunks, DocumentReference
from veri_agents_knowledgebase.utils import get_filter_from_config
import yaml

log = logging.getLogger(__name__)


class FixedKnowledgebaseQueryInput(BaseModel):
    query: str = Field(
        description="query to search for documents in the knowledgebase."
    )


class FixedKnowledgebaseQuery(BaseTool):
    """Search for documents in a knowledgebase that is not selected by the agent."""

    name: str = "knowledge_retrieval_fixed_kb"
    description: str = (
        "Searches for documents in a knowledgebase. Input should be a search query."
    )
    args_schema = FixedKnowledgebaseQueryInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    num_results: int = 10
    knowledgebase: Knowledgebase

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "kb_search_" + self.knowledgebase.name
        if not self.knowledgebase:
            raise ToolException(
                "Knowledgebase not specified (pass into get_tool as knowledgebase='kb')."
            )
        self.description = f"Searches for documents in the {self.knowledgebase.name} knowledgebase. Use this tool if you're interested in documents about {self.knowledgebase.description}."

    def _run(
        self,
        query: str,
        # knowledgebase: Annotated[str, InjectedState("knowledgebase")],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentChunks | Document]]:
        return_text = ""
        log.info("Searching in knowledgebase %s for %s", self.knowledgebase.name, query)
        docs_or_docs_chunks = list(self.knowledgebase.search(query, limit=self.num_results))
        
        log.debug(f"[FixedKnowledgebaseWithTagsQuery] Retrieved {len(docs_or_docs_chunks or [])} documents.")
        if not docs_or_docs_chunks:
            return_text += f"No documents found in the knowledgebase for query '{query}'."
        else:
            return_text = yaml.dump([doc_or_doc_chunks.model_dump() for doc_or_doc_chunks in docs_or_docs_chunks], sort_keys=False)

        return return_text, docs_or_docs_chunks



class FixedKnowledgebaseWithTagsQueryInput(BaseModel):
    query: str = Field(
        description="query to search for documents in the knowledgebase. Only use tags if you know they exist and definitely fit, otherwise prefer search without specifying tags."
    )
    tags_any: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected if they match any of the tags in this list. Useful if for example searching for a document that's either about 'electricity' or about 'software'.",
    )
    tags_all: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected if they match all of the tags in this list. Useful if for example searching for a document that's both a 'policy' and valid in 'Nashville'.",
    )
    documents: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected only if they match the document IDs in the list. Useful if you only want to search inside specific documents.",
    )


class FixedKnowledgebaseWithoutTagsQueryInput(BaseModel):
    query: str = Field(
        description="query to search for documents in the knowledgebase."
    )
    documents: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected only if they match the document IDs in the list. Useful if you only want to search inside specific documents.",
    )


class FixedKnowledgebaseWithTagsQuery(BaseTool):
    """Search for documents in a knowledgebase (that can not be selected by the agent) where the agent can specify tags to filter the documents."""

    name: str = "kb_search_tags"
    description: str = "Searches in documents."
    args_schema = FixedKnowledgebaseWithTagsQueryInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    num_results: int = 10
    knowledgebase: Knowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    runnable_config_filter_prefix: str = "filter_"
    """ The prefix to use for the filter in the runnable config. For example if the prefix is 'filter_' then it will pull from the config 'filter_tags_any', 'filter_tags_all', 'filter_documents' """

    allow_llm_filter: bool = True
    """ If True, the LLM can specify a filter in the prompt. If False, the filter is only set by the user through runnable config. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name = self.name + self.name_suffix.replace("-", "_")
        kb_tags = self.knowledgebase.tags
        self.description = f"Searches for documents in the {self.knowledgebase.name} knowledgebase. Use this tool if you're interested in documents about {self.knowledgebase.description}."
        if kb_tags and self.allow_llm_filter:
            self.description += " The knowledgebase has the following tags you can use when searching for information: "
            for k, v in kb_tags.items():
                if v:
                    v = f" ({v})"
                else:
                    v = ""
                self.description += f"'{k}'{v}, "
        else:
            self.args_schema = FixedKnowledgebaseWithoutTagsQueryInput

    def _create_filter(
        self,
        config: RunnableConfig,
        tags_any: Optional[list[str] | str] = None,
        tags_all: Optional[list[str] | str] = None,
        documents: Optional[list[str] | str] = None,
        out_llm_prompt: Optional[str] = None,
    ) -> KnowledgeFilter:
        """Create a filter for the knowledgebase from inputs and runnable config

        Args:
            config: A runnable config that might contain filter parameters.
            tags_any: If any of those tags are present in the document, it will be selected.
            tags_all: If all of those tags are present in the document, it will be selected.
            documents: If the document ID is in this list, it will be selected.
            out_llm_prompt: If provided, the filter will be added to this list for the LLM prompt so the LLM knows what has been filtered.
        """
        # filter set by the agent
        filter = KnowledgeFilter(
            docs=documents,
            tags_any_of=tags_any,
            tags_all_of=tags_all,
        )

        # if the user overrides fields using runnable config, use that instead
        if config:
            user_filter = get_filter_from_config(
                config,
                default_filter=filter,
                prefix=self.runnable_config_filter_prefix,
            )
            if user_filter != filter:
                filter = user_filter
                if out_llm_prompt is not None:
                    out_llm_prompt += "User applied the following filters: {user_filter}.\n"
        return filter

    def _run(
        self,
        query: str,
        config: RunnableConfig,
        tags_any: Optional[list[str] | str] = None,
        tags_all: Optional[list[str] | str] = None,
        documents: Optional[list[str] | str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentChunks | Document]]:
        return_text = ""
        
        filter = self._create_filter(
            config,
            tags_any=tags_any,
            tags_all=tags_all,
            documents=documents,
            out_llm_prompt=return_text,
        )
        log.info(
            "[FixedKnowledgebaseWithTagsQuery] Searching in knowledgebase %s for %s using filter %s",
            self.knowledgebase.name,
            query,
            filter,
        )
        docs_or_docs_chunks = list(self.knowledgebase.search(
            query, limit=self.num_results, filter=filter
        ))
        log.debug(f"[FixedKnowledgebaseWithTagsQuery] Retrieved {len(docs_or_docs_chunks or [])} documents.")
        if not docs_or_docs_chunks:
            return_text += f"No documents found in the knowledgebase for query '{query}'."
        else:
            return_text = yaml.dump([doc_or_doc_chunks.model_dump() for doc_or_doc_chunks in docs_or_docs_chunks], sort_keys=False)

        return return_text, docs_or_docs_chunks

    async def _arun(
        self,
        query: str,
        config: RunnableConfig,
        tags_any: Optional[list[str] | str] = None,
        tags_all: Optional[list[str] | str] = None,
        documents: Optional[list[str] | str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentChunks | Document]]:
        return_text = ""

        filter = self._create_filter(
            config,
            tags_any=tags_any,
            tags_all=tags_all,
            documents=documents,
            out_llm_prompt=return_text,
        )

        log.info(
            f"[FixedKnowledgebaseWithTagsQuery] Searching in knowledgebase {self.knowledgebase.name} for {query} using filter {filter}"
        )
        try:
            docs_or_docs_chunks = [doc async for doc in self.knowledgebase.asearch(
                query, limit=self.num_results, filter=filter
            )]
        except NotImplementedError:
            docs_or_docs_chunks = list(self.knowledgebase.search(
                query, limit=self.num_results, filter=filter
            ))
        
        log.debug(f"[FixedKnowledgebaseWithTagsQuery] Retrieved {len(docs_or_docs_chunks or [])} documents.")
        if not docs_or_docs_chunks:
            return_text += f"No documents found in the knowledgebase for query '{query}'."
        else:
            return_text = yaml.dump([doc_or_doc_chunks.model_dump() for doc_or_doc_chunks in docs_or_docs_chunks], sort_keys=False)

        return return_text, docs_or_docs_chunks


class FixedKnowledgebaseListDocumentsInput(BaseModel):
    tags_any: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected if they match any of the tags in this list. Useful if for example searching for a document that's either about 'electricity' or about 'software'.",
    )
    tags_all: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected if they match all of the tags in this list. Useful if for example searching for a document that's both a 'policy' and valid in 'Nashville'.",
    )


class FixedKnowledgebaseListDocuments(BaseTool):
    """List documents in a knowledgebase that is not selected by the agent."""

    name: str = "list_documents"
    description: str = "Lists documents in a knowledgebase"
    args_schema = FixedKnowledgebaseListDocumentsInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    knowledgebase: Knowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    runnable_config_filter_prefix: str = "filter_"
    """ The prefix to use for the filter in the runnable config. For example if the prefix is 'filter_' then it will pull from the config 'filter_tags_any', 'filter_tags_all' """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name = self.name + self.name_suffix.replace("-", "_")
        kb_tags = self.knowledgebase.tags
        self.description = (
            f"Lists the documents in the {self.knowledgebase.name} knowledgebase."
        )
        if kb_tags:
            self.description += " The knowledgebase has the following tags: "
            for k, v in kb_tags.items():
                self.description += f"{k}: {v}, "

    def _run(
        self,
        config: RunnableConfig,
        tags_any: Optional[list[str] | str] = None,
        tags_all: Optional[list[str] | str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentReference]]:
        log.debug("[FixedKnowledgebaseListDocuments] Listing documents")

        # filter set by the agent
        filter = KnowledgeFilter(
            docs=None,
            tags_any_of=tags_any,
            tags_all_of=tags_all,
        )

        # if the user overrides filter fields using runnable config, use that instead
        if config:
            filter = get_filter_from_config(
                config,
                default_filter=filter,
                prefix=self.runnable_config_filter_prefix,
            )

            print("KB RETRIEVAL RUNNABLE FILTER")
            print(filter)

        docs = list(self.knowledgebase.list_documents(filter))
        log.debug(f"[FixedKnowledgebaseListDocuments] Retrieved {len(docs or [])} documents.")
        return yaml.dump([doc.model_dump() for doc in docs], sort_keys=False), docs
    
    async def _arun(
        self,
        config: RunnableConfig,
        tags_any: Optional[list[str] | str] = None,
        tags_all: Optional[list[str] | str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentReference]]:
        log.debug("[FixedKnowledgebaseListDocuments] Listing documents")

        # filter set by the agent
        filter = KnowledgeFilter(
            docs=None,
            tags_any_of=tags_any,
            tags_all_of=tags_all,
        )

        # if the user overrides filter fields using runnable config, use that instead
        if config:
            filter = get_filter_from_config(
                config,
                default_filter=filter,
                prefix=self.runnable_config_filter_prefix,
            )

            print("KB RETRIEVAL RUNNABLE FILTER")
            print(filter)

        docs = [doc async for doc in self.knowledgebase.alist_documents(filter)]
        log.debug(f"[FixedKnowledgebaseListDocuments] Retrieved {len(docs or [])} documents.")
        return yaml.dump([doc.model_dump() for doc in docs], sort_keys=False), docs

class FixedKnowledgebaseRetrieveDocumentsInput(BaseModel):
    tags_any: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected if they match any of the tags in this list. Useful if for example searching for a document that's either about 'electricity' or about 'software'.",
    )
    tags_all: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected if they match all of the tags in this list. Useful if for example searching for a document that's both a 'policy' and valid in 'Nashville'.",
    )


class FixedKnowledgebaseRetrieveDocuments(BaseTool):
    """Retrieve documents in a knowledgebase that is not selected by the agent."""

    name: str = "retrieve_documents"
    description: str = "Retrieves documents in a knowledgebase"
    args_schema = FixedKnowledgebaseRetrieveDocumentsInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    knowledgebase: Knowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    runnable_config_filter_prefix: str = "filter_"
    """ The prefix to use for the filter in the runnable config. For example if the prefix is 'filter_' then it will pull from the config 'filter_tags_any', 'filter_tags_all' """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name = self.name + self.name_suffix.replace("-", "_")
        kb_tags = self.knowledgebase.tags
        self.description = (
            f"Retrieves specific documents' content in the {self.knowledgebase.name} knowledgebase."
        )
        if kb_tags:
            self.description += " The knowledgebase has the following tags: "
            for k, v in kb_tags.items():
                self.description += f"{k}: {v}, "

    def _run(
        self,
        config: RunnableConfig,
        documents: list[str] | str,
    ) -> Tuple[str, list[Document]]:
        # We tell the LLM if the user has specified any filters
        return_text = ""

        # filter set by the agent
        filter = KnowledgeFilter(
            docs=documents,
        )

        log.info(
            f"[FixedKnowledgebaseRetrieveDocuments] Retrieving documents in knowledgebase \"{self.knowledgebase.name}\" using user filter {filter}"
        )
        docs = list(self.knowledgebase.get_documents(
            filter=filter
        ))

        log.debug(f"[FixedKnowledgebaseRetrieveDocuments] Retrieved {len(docs or [])} documents.")
        if not docs:
            return_text = f"Unable to retrieve documents in the knowledgebase with ids: {documents}."
        else:
            return_text = yaml.dump([doc.model_dump() for doc in docs], sort_keys=False)

        return return_text, docs

    async def _arun(
        self,
        config: RunnableConfig,
        documents: list[str] | str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[Document]]:
        # We tell the LLM if the user has specified any filters
        return_text = ""

        # filter set by the agent
        filter = KnowledgeFilter(
            docs=documents,
        )

        log.info(
            f"[FixedKnowledgebaseRetrieveDocuments] Retrieving documents in knowledgebase \"{self.knowledgebase.name}\" using user filter {filter}"
        )
        try:
            docs = [item async for item in self.knowledgebase.aget_documents(
                filter=filter
            )]
        except NotImplementedError:
            docs = list(self.knowledgebase.get_documents(
                filter=filter
            ))
       
        log.debug(f"[FixedKnowledgebaseRetrieveDocuments] Retrieved {len(docs or [])} documents.")
        if not docs:
            return_text = f"Unable to retrieve documents in the knowledgebase with ids: {documents}."
        else:
            return_text = yaml.dump([doc.model_dump() for doc in docs], sort_keys=False)
        
        return return_text, docs
