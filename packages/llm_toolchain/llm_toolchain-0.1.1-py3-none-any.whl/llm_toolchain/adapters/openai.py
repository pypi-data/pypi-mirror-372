# file: adapters/openai.py (Final Path-Based Version)

import json
from typing import Any, List, Dict, Sequence, Union

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer

class OpenAIAdapter(BaseAdapter):
    """
    An adapter for OpenAI's models that uses path-based discovery to interact
    with the native 'openai' library.
    """

    def _get_run_strategies(self) -> List[Sequence[str]]:
        """Provides the attribute path to OpenAI's run method."""
        return [
            ("chat", "completions", "create")
        ]

    def _get_parse_strategies(self) -> List[Sequence[Union[str, int]]]:
        """Provides the attribute path to OpenAI's parsable message object."""
        return [
            ("choices", 0, "message")
        ]

    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Builds the request payload for the OpenAI Chat Completions API."""
        final_messages = []
        if self.system_prompt:
            final_messages.append({"role": "system", "content": self.system_prompt})
        final_messages.extend(messages)
        
        payload = {
            "messages": final_messages,
            "model": "gpt-4o",  # A sensible default
        }
        payload.update(kwargs)

        # Only add the 'tools' key if there are actual tools to send.
        if tools:
            payload["tools"] = tools
        
        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """
        Parses the OpenAI message object extracted by the BaseAdapter.
        The base class's `parse` method has already discovered and extracted
        the `message` object for us.
        """
        message_object = super().parse(response)
        results: list[ParseResult] = []
        
        try:
            # 1. Check for and add reasoning text / final answer
            if message_object.content and isinstance(message_object.content, str):
                content = message_object.content.strip()
                print(f"-> LLM Reasoning Step: {content}")
                results.append(FinalAnswer(content=content))

            # 2. Check for and process tool calls
            if message_object.tool_calls:
                tool_calls = []
                for tc in message_object.tool_calls:
                    try:
                        arguments = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {"error": f"Malformed JSON from LLM: {tc.function.arguments}"}

                    tool_calls.append(
                        ToolCall(id=tc.id, name=tc.function.name, args=arguments)
                    )
                
                if tool_calls:
                    # The assistant_message is the entire message object itself
                    assistant_message = message_object.model_dump(exclude_unset=True)
                    results.append((tool_calls, assistant_message))
            
            return results
        except (AttributeError, IndexError, Exception) as e:
            return [FinalAnswer(content=f"Failed to parse OpenAI response: {e}")]

    def generate_schema(self, tool: Tool) -> dict:
        """Generates the OpenAI-specific JSON schema for a given tool."""
        generic_schema = self._inspect_and_build_json_schema(tool)
        return {
            "type": "function",
            "function": {
                "name": generic_schema["name"],
                "description": generic_schema["description"],
                "parameters": generic_schema["parameters_schema"],
            },
        }