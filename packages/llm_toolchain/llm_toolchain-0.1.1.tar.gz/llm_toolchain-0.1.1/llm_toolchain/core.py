# file: core.py (Refactored for improved usability)

import json
from typing import Callable
import inspect

# These imports may vary based on the specific clients you support
from google import generativeai as genai
from openai import OpenAI

from .models import FinalAnswer, ParseResult, ToolCall

# --- The Tool Class and Decorator ---

class Tool:
    """A simpler wrapper that just holds the function and its signature."""
    def __init__(self, function: Callable):
        self.name = function.__name__
        self.description = inspect.getdoc(function)
        self.signature = inspect.signature(function)
        self.function = function

def tool(func: Callable) -> Tool:
    """The decorator now just wraps the function in the Tool class."""
    if not func.__doc__:
        raise ValueError("Tool function must have a docstring for its description.")
    return Tool(function=func)

# --- The Main Toolchain Class ---

class Toolchain:
    """
    The main orchestrator that manages tools and executes LLM-driven workflows.
    """

    def __init__(self, tools: list[Tool], llm_client: any, adapter: any = None):
        """
        Initializes the Toolchain with a list of tools and an LLM client.

        Args:
            tools: A list of Tool objects created with the @tool decorator.
            llm_client: An instantiated LLM client (e.g., OpenAI(), genai.GenerativeModel(...)).
        """
        self.tools = {t.name: t for t in tools}
        self.llm_client = llm_client
        self.messages = []
        if not adapter:
            self.adapter = self._get_adapter(llm_client)
        else:
            self.adapter = adapter

    def _get_adapter(self, llm_client):
        """A simple factory to get the appropriate adapter for a given client."""
        # This is a simplified example; a real implementation might be more robust.
        from .adapters import OpenAIAdapter
        if isinstance(llm_client, OpenAI):
            return OpenAIAdapter()
        if isinstance(llm_client, genai.GenerativeModel):
            from .adapters import GeminiAdapter
            return GeminiAdapter()
        # Fallback to the generic prompt adapter if no native client is matched
        from .adapters import PromptAdapter
        return PromptAdapter()

    # --- High-Level "Simple" Method ---

    def run(self, prompt: str, **llm_params) -> str:
        """
        The main high-level method. Handles the entire ReAct loop automatically.
        
        Accepts a prompt and passes any additional keyword arguments directly to the
        LLM, allowing for full control over parameters like 'model', 'temperature', etc.
        """
        if not self.messages:
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = self.messages + [{"role": "user", "content": prompt}]

        while True:
            tools_as_schema = [self.adapter.generate_schema(t) for t in self.tools.values()]
            
            response = self.adapter.chat(
                llm_client=self.llm_client,
                messages=messages,
                tools=tools_as_schema,
                **llm_params # Pass all extra parameters directly to the adapter
            )
            
            parsed_results = self.adapter.parse(response)

            final_answers = [r for r in parsed_results if isinstance(r, FinalAnswer)]
            tool_call_tuples = [r for r in parsed_results if not isinstance(r, FinalAnswer)]

            if tool_call_tuples:
                if final_answers:
                    full_text = "\n".join([answer.content for answer in final_answers])
                    print(f"LLM Message: {full_text}")

                tool_outputs = []
                for tool_calls, assistant_message in tool_call_tuples:
                    messages.append(assistant_message)
                    for tool_call in tool_calls:
                        output = self.execute_tool(tool_call)
                        tool_outputs.append(output)
                
                messages.extend(tool_outputs)
                continue

            if final_answers:
                return "\n".join([answer.content for answer in final_answers])

            return "The model did not provide a valid response."

    # --- Low-Level "Tinkering" Building Blocks ---
    
    def execute_tool(self, tool_call: ToolCall) -> dict:
        """Executes a single tool call and returns the formatted output."""
        if tool_call.name not in self.tools:
            return {"error": f"Tool '{tool_call.name}' not found."}

        try:
            tool_obj = self.tools[tool_call.name]
            output = tool_obj.function(**tool_call.args)
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": json.dumps(output),
            }
        except Exception as e:
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": f"Error executing tool: {e}",
            }