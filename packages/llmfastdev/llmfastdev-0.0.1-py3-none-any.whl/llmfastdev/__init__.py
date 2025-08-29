"""
llmfastdev - A Python client for interacting with llamafile local LLM instances.

This package provides easy-to-use client classes for communicating with llamafile servers.
"""

from .llamafile_client import LlamafileClient

__version__ = "0.0.1"
__all__ = ["LlamafileClient"]