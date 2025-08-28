import json
import logging
import asyncio
from datetime import datetime
from typing import (
    Any,
    Literal,
    NotRequired,
    Optional,
    Required,
    Sequence,
    Callable,
    Type,
    TypedDict,
    Union,
    Unpack,
    cast,
    overload,
)

from langchain_core.language_models import (
    LanguageModelLike,
)
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Checkpointer
from langgraph.prebuilt import ToolNode, create_react_agent
from langgraph.prebuilt.chat_agent_executor import (
    StructuredResponseSchema,
    Prompt,
    StateSchemaType,
)
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.utils.runnable import RunnableLike
from langgraph.store.base import BaseStore

from pydantic import BaseModel
from veri_agents_knowledgebase import Knowledgebase

log = logging.getLogger(__name__)


class CreateReactAgentKwargs(TypedDict, total=False):
    pre_model_hook: Optional[RunnableLike]
    state_schema: Optional[StateSchemaType]
    config_schema: Optional[Type[Any]]
    checkpointer: Optional[Checkpointer]
    store: Optional[BaseStore]
    interrupt_before: Optional[list[str]]
    interrupt_after: Optional[list[str]]
    debug: bool
    version: Literal["v1", "v2"]
    name: Optional[str]


class CreateQaAgentBaseKwargs(CreateReactAgentKwargs):
    llm: Required[LanguageModelLike]
    knowledgebases: Required[Sequence[Knowledgebase]]
    tools: NotRequired[Sequence[BaseTool | Callable] | None]


class CreateQaAgentKwargs(CreateQaAgentBaseKwargs):
    prompt: NotRequired[Optional[str]]
    response_format: NotRequired[Optional[
        Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]
    ]]


def create_qa_agent(
    **kwargs: Unpack[CreateQaAgentKwargs],
) -> CompiledGraph:
    tools: list[BaseTool | Callable] = list(*kwargs.pop("tools", []))
    knowledgebases: Sequence[Knowledgebase] = kwargs.pop(
        "knowledgebases"
    )  # pyright: ignore[reportAssignmentType]
    prompt: str | None = kwargs.pop(
        "prompt", None
    )  # pyright: ignore[reportAssignmentType]
    llm: LanguageModelLike = kwargs.pop("llm")  # pyright: ignore[reportAssignmentType]

    for _, knowledgebase in enumerate(knowledgebases):
        tools.extend(
            knowledgebase.get_tools(
                search_tools=True,
                list_tools=True,
                retrieve_tools=True,
                write_tools=False,
            )
        )
    tool_node = ToolNode(tools)

    prompt = (
        prompt or ""
    ) + f"""Today's date is: {datetime.now().strftime("%Y-%m-%d")}."""

    return create_react_agent(
        model=llm,
        tools=tool_node,
        prompt=prompt,
        **cast(CreateReactAgentKwargs, kwargs),
    )


def _resolve_structured_response_format(
    response_format: str | StructuredResponseSchema,
) -> StructuredResponseSchema:
    if isinstance(response_format, str):
        return json.loads(response_format)

    if isinstance(response_format, dict):
        response_format.setdefault("title", "QA_AdhocResult")
        response_format.setdefault("description", "")
        return response_format

    return response_format


type IndeterminateQaAgentResponseSchema = UntypedQaAgentResponseSchema | TypedQaAgentResponseSchema
type UntypedQaAgentResponseSchema = Union[dict, tuple[str, dict]]
type TypedQaAgentResponseSchema[R: BaseModel] = Union[type[R], tuple[str, type[R]]]


def _resolve_response_format(
    response_format: str | IndeterminateQaAgentResponseSchema,
) -> Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]:
    if isinstance(response_format, tuple):
        (prompt, inner_format) = response_format
        return (prompt, _resolve_structured_response_format(inner_format))

    return _resolve_structured_response_format(response_format)


@overload
async def qa(
    prompt: str,
    *,
    response_format: Optional[str | UntypedQaAgentResponseSchema] = None,
    retries: int = 3,
    config: RunnableConfig | None = None,
    system_prompt: Optional[str]= None,
    retry_delay: float = 3,
    **kwargs: Unpack[CreateQaAgentBaseKwargs],
) -> dict[str, Any]: ...
@overload
async def qa[R: BaseModel](
    prompt: str,
    *,
    response_format: TypedQaAgentResponseSchema[R],
    retries: int = 3,
    config: RunnableConfig | None = None,
    system_prompt: Optional[str]= None,
    retry_delay: float = 3,
    **kwargs: Unpack[CreateQaAgentBaseKwargs],
) -> R: ...
async def qa(
    prompt: str,
    *,
    response_format: Optional[str | IndeterminateQaAgentResponseSchema] = None,
    retries: int = 3,
    config: RunnableConfig | None = None,
    system_prompt: Optional[str]= None,
    retry_delay: float = 3,
    **kwargs: Unpack[CreateQaAgentBaseKwargs],
) -> dict[str, Any] | Any:
    response_format = (
        _resolve_response_format(response_format) if response_format else None
    )

    qa_snapshot_agent = create_qa_agent(
        response_format=response_format,
        prompt=system_prompt,
        **cast(dict, cast(CreateQaAgentKwargs, kwargs)),
    )

    exceptions: list[Exception] = []

    for retry in range(retries):
        try:
            res = await qa_snapshot_agent.ainvoke(
                input={"messages": [HumanMessage(content=prompt)]},
                config=config,
            )

            if response_format is None:
                return cast(
                    dict,
                    res,
                )[
                    "messages"
                ][-1].content
            else:
                structured_response: Any = cast(
                    dict,
                    res,
                )["structured_response"]

                if isinstance(response_format, type):
                    marshalled = cast(type[BaseModel], response_format).model_validate(structured_response, strict=False)

                    return marshalled
                else:
                    return structured_response
        except Exception as e:
            log.warning("QA (attempt %d): error: %s. Retrying...", retry, e)
            exceptions.append(e)
            await asyncio.sleep(retry_delay)

    raise ExceptionGroup(f"QA invocation failed after {retries} retries", exceptions)
