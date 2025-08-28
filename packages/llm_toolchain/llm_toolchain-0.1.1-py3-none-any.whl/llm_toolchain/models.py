from dataclasses import dataclass
from typing import Union


@dataclass
class ToolCall:
    """A data class representing a tool call requested by the LLM."""

    id: str
    name: str
    args: dict


@dataclass
class FinalAnswer:
    """A data class representing a final answer from the LLM."""

    content: str


# A type hint for the result of parsing an LLM response
ParseResult = Union[list[ToolCall], FinalAnswer]
