import inspect
from typing import get_type_hints


def generate_schema(func: callable) -> dict:
    """
    Generates a JSON schema for a function's parameters and description.

    This is a simplified implementation. A production version would handle
    more types, default values, and more complex docstrings.
    """
    if not func.__doc__:
        raise ValueError("Tool function must have a docstring for its description.")

    # Get the function signature
    sig = inspect.signature(func)

    # Get type hints
    type_hints = get_type_hints(func)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        param_type = type_hints.get(name, str).__name__
        properties[name] = {"type": param_type.lower()}
        if param.default is inspect.Parameter.empty:
            required.append(name)

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": inspect.getdoc(func),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }
