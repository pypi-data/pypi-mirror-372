# file: adapters/gemini.py (Final Path-Based Version)

import json
from typing import Any, List, Dict, Sequence, Union

# Lazy-import and error message can be handled at the top level
try:
    from google.generativeai import types
except ImportError:
    raise ImportError(
        "To use the GeminiAdapter, please run 'pip install toolchain[gemini]' "
        "or 'pip install google-generativeai'."
    )

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer

class GeminiAdapter(BaseAdapter):
    """
    An adapter for Google's Gemini models that uses path-based discovery
    to interact with the native google-generativeai library.
    """

    def _get_run_strategies(self) -> List[Sequence[str]]:
        """Provides the attribute path to Gemini's run method."""
        return [
            ("generate_content",)
        ]

    def _get_parse_strategies(self) -> List[Sequence[Union[str, int]]]:
        """Provides the attribute path to Gemini's parsable content."""
        return [
            ("candidates", 0, "content", "parts")
        ]

    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Builds the request payload for the Gemini generate_content API."""
        contents = self._format_contents(messages)
        
        generation_config = kwargs.copy()
        if 'max_tokens' in generation_config:
            generation_config['max_output_tokens'] = generation_config.pop('max_tokens')

        # --- Start of the Fix ---
        payload = {
            "contents": contents,
            "generation_config": generation_config,
        }

        # Only add the 'tools' key to the payload if the tools list is not empty.
        if tools:
            gemini_tools = types.Tool(function_declarations=tools)
            payload["tools"] = [gemini_tools]
        
        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """
        Parses the Gemini response content extracted by the BaseAdapter.
        The base class's `parse` method has already discovered and extracted
        the `parts` list for us.
        """
        all_parts = super().parse(response)
        results: list[ParseResult] = []
        
        try:
            tool_calls_list = []
            reasoning_text_parts = []

            for part in all_parts:
                if hasattr(part, 'text') and part.text:
                    reasoning_text_parts.append(part.text.strip())
                
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    arguments = dict(fc.args)
                    tool_call_id = f"call_{fc.name}_{len(tool_calls_list)}"
                    tool_calls_list.append(
                        ToolCall(id=tool_call_id, name=fc.name, args=arguments)
                    )

            if reasoning_text_parts:
                full_reasoning = "\n".join(reasoning_text_parts)
                print(f"-> LLM Reasoning Step: {full_reasoning}")
                results.append(FinalAnswer(content=full_reasoning))

            if tool_calls_list:
                # Reconstruct the original full response message for history
                assistant_message = type(response.candidates[0].content).to_dict(response.candidates[0].content)
                results.append((tool_calls_list, assistant_message))

            return results
        except (AttributeError, IndexError, TypeError, Exception) as e:
            return [FinalAnswer(content=f"Failed to parse Gemini response: {e}")]

    def generate_schema(self, tool: Tool) -> dict:
        """Generates the Gemini-specific JSON schema for a given tool."""
        generic_schema = self._inspect_and_build_json_schema(tool)
        return {
            "name": generic_schema["name"],
            "description": generic_schema["description"],
            "parameters": generic_schema["parameters_schema"],
        }

    def _format_contents(self, messages: list[dict]) -> list[dict]:
        """
        A helper to convert the generic message history into the list of
        dictionaries that the Gemini API expects.
        """
        contents = []
        if self.system_prompt:
            contents.append({"role": "user", "parts": [{"text": self.system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else msg.get("role")
            
            if role == "tool":
                part = {
                    "function_response": {
                        "name": msg.get("name"),
                        "response": {"content": json.loads(msg.get("content", '""'))}
                    }
                }
                contents.append({"role": "user", "parts": [part]})
            elif "parts" in msg:
                contents.append({"role": "model", "parts": msg["parts"]})
            else:
                part = {"text": msg.get("content", "")}
                contents.append({"role": role, "parts": [part]})
        
        return contents