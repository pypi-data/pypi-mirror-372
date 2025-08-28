# file: base.py (Corrected Final Version)

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict, get_type_hints, Sequence, Union
import inspect

# These imports depend on your project structure
from ..core import Tool
from ..models import ParseResult

class BaseAdapter(ABC):
    """
    An abstract base class for creating adapters. It discovers how to interact
    with an LLM client by traversing lists of possible attribute paths for
    running a call and parsing a response.
    """
    def __init__(
        self,
        system_prompt: str | None = None,
        manual_run_path: Sequence[str] | None = None,
        manual_parse_path: Sequence[Union[str, int]] | None = None,
    ):
        self.system_prompt = system_prompt
        # Caching for discovered callables
        self._run_callable: Callable | None = manual_run_path
        self._parse_callable: Callable | None = manual_parse_path
    
    # --- Abstract methods for subclasses ---

    @abstractmethod
    def _get_run_strategies(self) -> List[Sequence[str]]:
        """Subclasses must provide a list of possible attribute paths to the run method."""
        pass

    @abstractmethod
    def _get_parse_strategies(self) -> List[Sequence[Union[str, int]]]:
        """Subclasses must provide a list of possible attribute paths to the parseable content."""
        pass

    @abstractmethod
    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Subclasses must build the model-specific request payload."""
        pass
    
    # --- Helper for traversing paths ---

    def _traverse_path(self, obj: Any, path: Sequence[Union[str, int]]) -> Any:
        """Dynamically accesses a value in a nested object or attribute chain."""
        for key in path:
            obj = obj[key] if isinstance(key, int) else getattr(obj, key)
        return obj

    # --- Discovery Logic ---

    def _discover_run_callable_if_needed(self, llm_client: Any, test_payload: dict):
        if self._run_callable and isinstance(self._run_callable, Callable): return
        
        print("--- Discovering LLM run path... ---")
        strategies = [self._run_callable] if self._run_callable else self._get_run_strategies()
        
        for path in strategies:
            try:
                method = self._traverse_path(llm_client, path)
                if callable(method):
                    method(**test_payload)
                    self._run_callable = method
                    print(f"--- Run path discovered: client.{'.'.join(path)} ---")
                    return
            except (AttributeError, TypeError, IndexError, KeyError):
                continue
        raise NotImplementedError("Could not discover a valid run path for the LLM client.")

    def _discover_parse_callable_if_needed(self, response: Any):
        if self._parse_callable and isinstance(self._parse_callable, Callable): return

        print("--- Discovering LLM parse path... ---")
        strategies = [self._parse_callable] if self._parse_callable else self._get_parse_strategies()

        for path in strategies:
            try:
                content = self._traverse_path(response, path)
                self._parse_callable = lambda resp: self._traverse_path(resp, path)
                print(f"--- Parse path discovered: response.{'.'.join(map(str, path))} ---")
                return
            except (AttributeError, TypeError, IndexError, KeyError):
                continue
        raise NotImplementedError("Could not discover a valid parse path for the response object.")

    # --- Core Orchestration ---

    def chat(self, llm_client: Any, messages: list[dict], tools: list[dict], **kwargs) -> Any:
        test_kwargs = kwargs.copy()
        test_kwargs.setdefault('max_tokens', 2)
        test_payload = self._build_request(messages, [], **test_kwargs)
        self._discover_run_callable_if_needed(llm_client, test_payload)

        request_payload = self._build_request(messages, tools, **kwargs)
        return self._run_callable(**request_payload)

    def parse(self, response: Any) -> Any:
        """Discovers the parse path and extracts the relevant content."""
        self._discover_parse_callable_if_needed(response)
        return self._parse_callable(response)

    # --- Start of Added Methods ---

    def _inspect_and_build_json_schema(self, tool: Tool) -> dict:
        """
        A universal helper to inspect a Tool and build a generic
        JSON Schema representation of its parameters.
        """
        type_hints = get_type_hints(tool.function)
        properties = {}
        required = []

        for name, param in tool.signature.parameters.items():
            py_type = type_hints.get(name, str)
            
            if py_type is str:
                properties[name] = {"type": "string"}
            elif py_type is int:
                properties[name] = {"type": "integer"}
            elif py_type is float:
                properties[name] = {"type": "number"}
            elif py_type is bool:
                properties[name] = {"type": "boolean"}
            else:
                properties[name] = {"type": "string"}

            if param.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "name": tool.name,
            "description": tool.description,
            "parameters_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    @abstractmethod
    def generate_schema(self, tool: Tool) -> Any:
        """Generates the model-specific schema for a given tool."""
        pass
    
    # --- End of Added Methods ---