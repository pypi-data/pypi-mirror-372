import logging
from typing import Annotated, Callable, List, Optional, Sequence, TypedDict, cast

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from veri_agents_knowledgebase import Knowledgebase, KnowledgeFilter
from veri_agents_knowledgebase.utils import get_filter_from_config, aprocess_docs

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

Entities = dict[str, list[str]]
EntitiesPerDocument = dict[str, Entities]


class ExtractionResponse(BaseModel):
    """Extracted information from documents"""

    entities: Entities = Field(
        description="Entities extracted from the documents. If you can't find any occurrences of the requested entity, return an empty list for that entity. DO NOT call this tool with the provided examples. Don't return multiple variants of the same entity like 'employee' and 'employees'. Type of field is JSON object with keys corresponding to entity type, and values of entity name with type string. NOT A STRING",
        examples=[
            {
                "persons": [
                    "John Doe",
                    "Jane James",
                    "S1 (Construction Superintendent)",
                ],
                "objects": ["excavator", "dog"],
            },
            {
                "locations": ["New York", "Los Angeles"],
                "dates": ["2025-02-05", "2025-03-10"],
            },
        ],
    )


def reduce_extraction_responses(
    existing: Entities | None, new: ExtractionResponse
) -> Entities:
    """Reduce two extraction responses by merging their entities."""
    if existing is None:
        existing = Entities()
    for entity_type, entities in new.entities.items():
        if entity_type not in existing:
            existing[entity_type] = []
        # Add only new entities (avoid duplicates)
        for entity in entities:
            if entity not in existing[entity_type]:
                existing[entity_type].append(entity)
    return existing


class ExtractInputSchema(BaseModel):
    """Input schema for the extract workflow"""

    knowledgebase: Optional[str] = Field(
        default=None,
        description="Knowledgebase to extract from",
        examples=["knowledgebase1", "knowledgebase2"],
    )
    filter_documents: List[str] = Field(
        default=[],
        description="Extract just within the list of documents with the given IDs.",
        examples=[["source1", "source2"]],
    )
    filter_tags_any: List[str] = Field(
        default=[],
        description="Extract entities from documents matching any of the given tags.",
        examples=[["finance", "priority_high"]],
    )
    filter_tags_all: List[str] = Field(
        default=[],
        description="Extract entities from documents matching all of the given tags.",
        examples=[["finance", "priority_high"]],
    )
    llm: Optional[str] = Field(
        default=None,
        description="LLM to use for extraction",
        examples=["nova_pro", "bedrock_claude_sonnet_37"],
    )


class ExtractOutputSchema(BaseModel):
    """Output schema for the extract workflow"""

    content: str = Field(
        description="Short summary of the entities",
        examples=[
            "The following entities were extracted: John Doe, Jane James, excavator"
        ],
    )
    entities: EntitiesPerDocument = Field(
        default={},
        description="Extracted entities. Dictionary of documents to entities where entities are a dictionary of entity types to list of entities",
    )


class AgentState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    documents: EntitiesPerDocument


def create_extract_agent(
    extract_llm: BaseLanguageModel | Callable[[RunnableConfig], BaseLanguageModel],
    knowledgebase: Knowledgebase | Callable[[RunnableConfig], Knowledgebase],
    filter: KnowledgeFilter | None = None,
    system_prompt: str | None = None,
    summarize_prompt: str | None = None,
) -> CompiledGraph:
    if system_prompt is None:
        system_prompt = "Your job is to identify important entities, aspects, key points, incidents etc. in the provided data. only use the provided context, don't use your internal knowledge to make up things."
    if summarize_prompt is None:
        summarize_prompt = "Summarize your findings about the extracted entities from the documents: \n"

    async def aextract(state: AgentState, config: RunnableConfig) -> AgentState:
        """LangGraph node to extract entities from the documents"""
        try:
            messages = state["messages"]
            log.debug(f"Extract: Runnable config: {config}")
            runnable_filter = get_filter_from_config(config, filter, prefix="filter_")
            runnable_kb = (
                knowledgebase(config) if callable(knowledgebase) else knowledgebase
            )
            runnable_llm = (
                extract_llm(config)
                if not isinstance(extract_llm, BaseLanguageModel)
                else extract_llm
            )
            log.debug(f"Extract: entities with filter: {runnable_filter}")
            docs = runnable_kb.get_documents(runnable_filter)
            llm_structured = runnable_llm.with_structured_output(ExtractionResponse)

            extraction_results = await aprocess_docs(
                docs,
                messages,
                llm_structured,
                system_prompt=system_prompt,
                reduce_results=reduce_extraction_responses,
                max_concurrent_docs=3,
                max_concurrent_chunks=3,
            )
            extraction_results = cast(EntitiesPerDocument, extraction_results)
            artifact = {
                "type": "json",
                "source": "extracted_entities",
                "documents": extraction_results,
            }
            return {
                "messages": [
                    ToolMessage(
                        "Extraction complete.",
                        tool_call_id="extract",
                        artifact=artifact,
                    )
                ],
                "documents": extraction_results,
            }
        except Exception as e:
            log.error("Error in extract: ", exc_info=True)
            return {
                "messages": [AIMessage(content="Error in extraction: " + str(e))],
                "documents": {},
            }

    async def asummarize(state: AgentState, config: RunnableConfig) -> AgentState:
        """LangGraph node to summarize the extracted entities from previous nodes."""
        runnable_llm = (
            extract_llm(config)
            if not isinstance(extract_llm, BaseLanguageModel)
            else extract_llm
        )
        try:
            messages = state["messages"]
            send_messages = [
                SystemMessage(content=system_prompt),
                messages[-2],  # the user input
                HumanMessage(content=summarize_prompt + str(state["documents"])),
            ]

            response = await runnable_llm.ainvoke(send_messages)
            output = ExtractOutputSchema(
                content=response.content,
                entities=state["documents"],
            )

            return {
                "messages": [
                    AIMessage(
                        content=output.model_dump_json(),
                    )
                ],
                "documents": state["documents"],
            }
        except Exception as e:
            log.error("Error in summarize: ", exc_info=True)
            output = ExtractOutputSchema(
                content="Error in summarization: " + str(e),
                entities=state["documents"],
            )
            return {
                "messages": [AIMessage(content=output.model_dump_json())],
                "documents": state["documents"],
            }

    graph = StateGraph(AgentState)
    graph.add_node("extract", aextract)
    graph.add_node("summarize", asummarize)

    graph.add_edge(START, "extract")
    graph.add_edge("extract", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()
