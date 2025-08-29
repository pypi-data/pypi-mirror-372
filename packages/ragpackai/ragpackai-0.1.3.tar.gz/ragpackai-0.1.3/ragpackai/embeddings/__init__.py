"""
Embedding provider wrappers for ragpackai.

This module provides convenient wrapper classes for different embedding providers
with consistent interfaces and lazy imports.
"""

from .openai import OpenAI
from .huggingface import HuggingFace
from .google import Google

__all__ = ["OpenAI", "HuggingFace", "Google"]
