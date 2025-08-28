# In toolchain/adapters/__init__.py

"""
This file makes the primary adapter classes directly importable
from the `toolchain.adapters` package, creating a clean public API.
"""

from .base import BaseAdapter
from .gemini import GeminiAdapter
from .openai import OpenAIAdapter


# Optional: You can also control what `from .adapters import *` does
__all__ = [
    "BaseAdapter",
    "OpenAIAdapter",
    "GeminiAdapter",
    "PromptAdapter",
]
