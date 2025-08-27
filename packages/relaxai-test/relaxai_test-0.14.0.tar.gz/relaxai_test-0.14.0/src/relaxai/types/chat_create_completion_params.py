# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .stream_options_param import StreamOptionsParam
from .function_definition_param import FunctionDefinitionParam
from .chat_completion_message_param import ChatCompletionMessageParam

__all__ = [
    "ChatCreateCompletionParams",
    "Prediction",
    "ResponseFormat",
    "ResponseFormatJsonSchema",
    "Tool",
    "WebSearchOptions",
    "WebSearchOptionsUserLocation",
    "WebSearchOptionsUserLocationApproximate",
]


class ChatCreateCompletionParams(TypedDict, total=False):
    messages: Required[Iterable[ChatCompletionMessageParam]]

    model: Required[str]

    query_stream: Annotated[bool, PropertyInfo(alias="stream")]
    """If true, server responds as an SSE stream.

    Generators may produce an ergonomic streaming method when this is set.
    """

    chat_template_kwargs: object

    frequency_penalty: float

    function_call: object

    functions: Iterable[FunctionDefinitionParam]

    logit_bias: Dict[str, int]

    logprobs: bool

    max_completion_tokens: int

    max_tokens: int

    metadata: Dict[str, str]

    n: int

    parallel_tool_calls: object

    prediction: Prediction

    presence_penalty: float

    reasoning_effort: str

    response_format: ResponseFormat

    seed: int

    stop: List[str]

    store: bool

    body_stream: Annotated[bool, PropertyInfo(alias="stream")]

    stream_options: StreamOptionsParam

    temperature: float

    tool_choice: object

    tools: Iterable[Tool]

    top_logprobs: int

    top_p: float

    user: str

    web_search_options: WebSearchOptions


class Prediction(TypedDict, total=False):
    content: Required[str]

    type: Required[str]


class ResponseFormatJsonSchema(TypedDict, total=False):
    name: Required[str]

    strict: Required[bool]

    description: str


class ResponseFormat(TypedDict, total=False):
    json_schema: ResponseFormatJsonSchema

    type: str


class Tool(TypedDict, total=False):
    type: Required[str]

    function: FunctionDefinitionParam


class WebSearchOptionsUserLocationApproximate(TypedDict, total=False):
    city: str

    country: str

    latitude: float

    longitude: float

    state: str


class WebSearchOptionsUserLocation(TypedDict, total=False):
    approximate: WebSearchOptionsUserLocationApproximate

    type: str


class WebSearchOptions(TypedDict, total=False):
    search_context_size: int

    user_location: WebSearchOptionsUserLocation
