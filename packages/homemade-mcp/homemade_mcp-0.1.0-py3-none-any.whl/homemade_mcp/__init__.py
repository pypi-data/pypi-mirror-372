# -*- coding: utf-8 -*-
# src/homemade_mcp/__init__.py
"""Homemade-MCP package version and public surface."""

from .client import LLMClient
from .schemas import StdRequest, LLMInput, OCRInput

__version__ = "0.1.0"
__all__ = ["LLMClient", "StdRequest", "LLMInput", "OCRInput"]
