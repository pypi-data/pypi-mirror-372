# file: adapters/prompt.py (Simplified with Dual Formatting)

import json
import re
from typing import Any, List, Dict, Sequence, Union

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer

class PromptAdapter(BaseAdapter):
    """
    A generic adapter that emulates tool-calling for LLMs without native support
    by injecting instructions into the system prompt. It uses path-based discovery
    to find the correct methods to call on common LLM clients.
    """

    def _get_run_strategies(self) -> List[Sequence[str]]:
        """Provides common run paths for different clients."""
        return [
            ("chat", "completions", "create"), # OpenAI
            ("messages", "create"),           # Anthropic
            ("generate_content",)             # Gemini
        ]

    def _get_parse_strategies(self) -> List[Sequence[Union[str, int]]]:
        """Provides common parse paths for the text content from different clients."""
        return [
            ("choices", 0, "message", "content"), # OpenAI
            ("content", 0, "text"),               # Anthropic
            ("text",)                             # Gemini
        ]

    def _build_request(self, messages: list[dict], tools: list[str], **kwargs) -> dict:
        """
        Injects the tool-use prompt and builds a universal payload containing
        both 'messages' and 'contents' formats to ensure compatibility.
        """
        instruction_prompt = f"""
You are a helpful assistant with access to a set of tools.
## AVAILABLE TOOLS:
{"\n".join(tools)}
## RESPONSE INSTRUCTIONS:
When you decide to call one or more tools, you MUST respond with ONLY a single, valid JSON object. Your entire response must be the JSON object. The JSON object must conform to this exact schema: {{"tool_calls": [{{"tool_name": "<tool_name>", "arguments": {{"<arg_name": "<arg_value>"}}}}]}}
If you do not need to call any tools, provide a final, natural language answer to the user.
"""
        # --- Start of the Fix ---
        # 1. Create the standard 'messages' list for OpenAI/Anthropic
        final_messages = [{"role": "system", "content": instruction_prompt}]
        final_messages.extend(messages)

        # 2. Create the 'contents' list for Gemini
        contents = []
        for msg in final_messages:
            role = "model" if msg.get("role") in ["assistant", "system"] else "user"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
        
        # 3. Build a payload containing BOTH formats, plus other params
        payload = {
            # "messages": final_messages,
            "contents": contents,
            "generation_config": kwargs.copy()
        }
        payload.update(kwargs)
        # --- End of the Fix ---
        
        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """
        Parses the raw text content extracted by the BaseAdapter's discovery.
        """
        response_text = super().parse(response)
        
        if not response_text or not isinstance(response_text, str):
            return [FinalAnswer(content=str(response_text))]

        print(f"-> LLM Reasoning Step: {response_text.strip()}")
        results: list[ParseResult] = [FinalAnswer(content=response_text)]
        
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_string = match.group(0)
            try:
                parsed_json = json.loads(json_string)
                tool_calls_data = parsed_json.get("tool_calls")
                if isinstance(tool_calls_data, list):
                    tool_calls_list = []
                    for call_data in tool_calls_data:
                        tool_name = call_data.get("tool_name")
                        arguments = call_data.get("arguments")
                        if isinstance(tool_name, str) and isinstance(arguments, dict):
                            tool_call_id = f"call_{tool_name}_{len(tool_calls_list)}"
                            tool_calls_list.append(ToolCall(id=tool_call_id, name=tool_name, args=arguments))
                    
                    if tool_calls_list:
                        assistant_message = {"role": "assistant", "content": json_string}
                        results.append((tool_calls_list, assistant_message))
            except json.JSONDecodeError:
                pass
            
        return results

    def generate_schema(self, tool: Tool) -> str:
        """
        Generates a simple, human-readable string representation of the tool
        for injection into the prompt.
        """
        generic_schema = self._inspect_and_build_json_schema(tool)
        params = [f'{name}: {schema.get("type", "any")}' for name, schema in generic_schema["parameters_schema"]["properties"].items()]
        param_str = ", ".join(params)
        return f"- {generic_schema['name']}({param_str}): {generic_schema['description']}"