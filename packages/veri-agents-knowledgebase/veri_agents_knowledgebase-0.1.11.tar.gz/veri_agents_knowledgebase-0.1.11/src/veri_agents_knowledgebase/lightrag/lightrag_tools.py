import logging
from typing import Optional, Tuple

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool, ToolException
from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel, Field
from veri_agents_knowledgebase.knowledgebase import GraphKnowledgebase

log = logging.getLogger(__name__)


class LightRAGQueryInput(BaseModel):
    high_level_keywords: str = Field(
        description="High level search query keywords focus on overarching concepts or themes"
    )
    low_level_keywords: str = Field(
        description="Low level search query keywords focus on specific entities, details, or concrete terms."
    )
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "Query: How does international trade influence global economic stability?",
                    "value": {
                        "high_level_keywords": [
                            "International trade",
                            "Global economic stability",
                            "Economic impact",
                        ],
                        "low_level_keywords": [
                            "Trade agreements",
                            "Tariffs",
                            "Currency exchange",
                            "Imports",
                            "Exports",
                        ],
                    },
                },
                {
                    "description": "Query: What are the environmental consequences of deforestation on biodiversity?",
                    "value": {
                        "high_level_keywords": [
                            "Environmental consequences",
                            "Deforestation",
                            "Biodiversity loss",
                        ],
                        "low_level_keywords": [
                            "Species extinction",
                            "Habitat destruction",
                            "Carbon emissions",
                            "Rainforest",
                            "Ecosystem",
                        ],
                    },
                },
                {
                    "description": "Query: What is the role of education in reducing poverty?",
                    "value": {
                        "high_level_keywords": [
                            "Education",
                            "Poverty reduction",
                            "Socioeconomic development",
                        ],
                        "low_level_keywords": [
                            "School access",
                            "Literacy rates",
                            "Job training",
                            "Income inequality",
                        ],
                    },
                },
            ]
        }
    }


class LightRAGQuery(BaseTool):
    """Search for documents in a LightRAG knowledgebase."""

    name: str = "kb_retrieve_lightrag"
    description: str = "Retrieves data from a knowledge graph based knowledge base."
    args_schema = LightRAGQueryInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    num_results: int = 5
    knowledgebase: GraphKnowledgebase
    """ The knowledgebase to retrieve from. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name = self.name + self.name_suffix.replace("-", "_")

    async def _run(
        self,
        config: RunnableConfig,
        high_level_keywords: str,
        low_level_keywords: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[list[str], dict]:
        log.info(
            f"[LightRAGQuery] Searching in knowledgebase for high level keywords {high_level_keywords} and low level keywords {low_level_keywords}"
        )
        return_texts = []
        try:
            ret_text, ret_graph = self.knowledgebase.graph_retrieve(
                "",
                limit=self.num_results,
                high_level_keywords=high_level_keywords,
                low_level_keywords=low_level_keywords,
            )
        except Exception as e:
            log.error(f"Error during knowledgebase retrieval: {e}")
            raise ToolException(f"Error during knowledgebase retrieval: {e}")

        if not ret_text:
            return_texts.append("No documents found in the knowledgebase.")
        else:
            return_texts.append(ret_text)
        return return_texts, {
            "items": ret_graph,
            "type": "graph",
            "source": "knowledgebase",
        }

    async def _arun(
        self,
        config: RunnableConfig,
        high_level_keywords: str,
        low_level_keywords: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[list[str], dict]:
        log.info(
            f"[LightRAGQuery] Searching in knowledgebase for high level keywords {high_level_keywords} and low level keywords {low_level_keywords}"
        )
        return_texts = []
        try:
            ret_text, ret_graph = await self.knowledgebase.agraph_retrieve(
                "",
                limit=self.num_results,
                high_level_keywords=high_level_keywords,
                low_level_keywords=low_level_keywords,
            )
        except Exception as e:
            log.error(f"Error during knowledgebase retrieval: {e}")
            raise ToolException(f"Error during knowledgebase retrieval: {e}")

        if not ret_text:
            return_texts.append("No documents found in the knowledgebase.")
        else:
            return_texts.append(ret_text)
        return return_texts, {
            "items": ret_graph,
            "type": "graph",
            "source": "knowledgebase",
        }


# TODO: add tools to get documents, entities etc.

# class FixedKnowledgebaseListDocumentsInput(BaseModel):
#     tags_any: Optional[list[str]|str] = Field(
#         default=None,
#         description="Documents are selected if they match any of the tags in this list. Useful if for example searching for a document that's either about 'electricity' or about 'software'.",
#     )
#     tags_all: Optional[list[str]|str] = Field(
#         default=None,
#         description="Documents are selected if they match all of the tags in this list. Useful if for example searching for a document that's both a 'policy' and valid in 'Nashville'.",
#     )


# class FixedKnowledgebaseListDocuments(BaseTool):
#     """List documents in a knowledgebase that is not selected by the agent.
#     """

#     name: str = "list_documents"
#     description: str = "Lists documents in a knowledgebase"
#     args_schema = FixedKnowledgebaseListDocumentsInput
#     # response_format: str = "content_and_artifact"  # type: ignore
#     handle_tool_errors: bool = True
#     knowledgebase: Knowledgebase
#     """ The knowledgebase to list documents from. This is passed in when the tool is created. """

#     name_suffix: str | None = None
#     """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

#     runnable_config_filter_prefix: str = "filter_"
#     """ The prefix to use for the filter in the runnable config. For example if the prefix is 'filter_' then it will pull from the config 'filter_tags_any', 'filter_tags_all' """

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         if self.name_suffix:
#             self.name = self.name + self.name_suffix.replace("-", "_")
#         kb_tags = self.knowledgebase.tags
#         self.description = (
#             f"Lists the documents in the {self.knowledgebase.name} knowledgebase."
#         )
#         if kb_tags:
#             self.description += " The knowledgebase has the following tags: "
#             for k, v in kb_tags.items():
#                 self.description += f"{k}: {v}, "

#     def _run(
#         self,
#         config: RunnableConfig,
#         tags_any: Optional[list[str]|str] = None,
#         tags_all: Optional[list[str]|str] = None,
#         run_manager: Optional[CallbackManagerForToolRun] = None,
#     ) -> str:  # -> Tuple[list[str], dict]:
#         # TODO: would be interesting to not get the content as well
#         log.debug("[FixedKnowledgebaseListDocuments] Listing documents")

#         # filter set by the agent
#         filter = KnowledgeFilter(
#             docs=None,
#             tags_any_of=tags_any,
#             tags_all_of=tags_all,
#         )

#         # if the user overrides filter fields using runnable config, use that instead
#         if config:
#             filter = get_filter_from_config(
#                 config,
#                 default_filter=filter,
#                 prefix=self.runnable_config_filter_prefix,
#             )

#             print("KB RETRIEVAL RUNNABLE FILTER")
#             print(filter)

#         docs = self.knowledgebase.get_documents(filter)
#         log.debug("[FixedKnowledgebaseListDocuments] Retrieved documents.")
#         return str(
#             [
#                 (
#                     d.metadata.get("source"),
#                     d.metadata.get("doc_name"),
#                     d.metadata.get("last_updated"),
#                     d.metadata.get("tags"),
#                     d.metadata.get("summary"),
#                 )
#                 for d in docs
#             ]
#         )
