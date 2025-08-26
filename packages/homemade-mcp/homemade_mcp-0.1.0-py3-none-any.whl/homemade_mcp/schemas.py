# -*- coding: utf-8 -*-
# src/homemade_mcp/schemas.py
"""Unified request/response Pydantic schemas for Homemade-MCP.

These models define the single I/O contract used by `LLMClient` and all
adapters. External callers should only construct and consume these models,
never provider-specific payloads.
"""

from typing import Any, Dict, List, Literal, Optional, Sequence, Union

from PIL.Image import Image as PILImage
from pydantic import BaseModel, ConfigDict, Field


class PDFDoc(BaseModel):
    """Lightweight descriptor for a PDF document used in LLM blocks.

    Only local file paths are supported in v1 to keep the implementation
    lightweight. Use `pages` to restrict to specific 0-based page indexes.
    """

    source: str  # local file path
    pages: Optional[Sequence[int]] = None
    max_pages: int = 20


Block = Union[str, PILImage, PDFDoc]


class LLMInput(BaseModel):
    """Inputs for text and multimodal LLM tasks.

    - `blocks` is an ordered sequence of strings, PIL images, and `PDFDoc`
      that will be transformed into a single user message with multipart
      content. PDF docs are extracted to text via a lightweight parser.
    - `json_schema` enables structured outputs when supported by a provider.
    - `thinking` toggles reasoning budget/effort where available.
    - `search` toggles Gemini grounding.
    - `params` carries provider-agnostic generation parameters.
    """
    
    # PIL.Image.Image is an arbitrary Python type with no built-in schema, we need to allow it
    model_config = ConfigDict(arbitrary_types_allowed=True)

    blocks: Sequence[Block]  # e.g. ["Describe:", img, "Count items."]
    json_schema: Optional[Dict[str, Any]] = None  # structured output
    thinking: Optional[Literal["off", "low", "medium", "high", "auto"]] = "off"
    search: Optional[bool] = False  # Gemini grounding toggle
    params: Dict[str, Any] = Field(default_factory=dict)  # temp, max_tokens, etc.


class OCRInput(BaseModel):
    """Inputs for OCR extraction tasks.

    Minimal v1 shape: a single URL or file path. PDFs are allowed. You can
    optionally specify pages to process.
    """
    
    # PIL.Image.Image is an arbitrary Python type with no built-in schema, we need to allow it
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # simplest form: a single URL or path; you can extend later for PDFs, pages, bbox, etc.
    source: Union[str, PILImage]  # url or file path (PDFs allowed) or PIL image
    pages: Optional[Sequence[int]] = None
    params: Dict[str, Any] = Field(default_factory=dict)


class StdRequest(BaseModel):
    """Standard request envelope shared by all providers.

    Select a `provider`, `model`, and `task` and pass the corresponding
    input model (`LLMInput` or `OCRInput`).
    """

    provider: Literal["openai", "gemini", "mistral_ocr"]
    model: str
    task: Literal["llm", "ocr"]
    input: Union[LLMInput, OCRInput]


class Usage(BaseModel):
    """Optional usage and cost metadata when provided by a backend."""

    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: Optional[float] = None
    raw: Dict[str, Any] = Field(default_factory=dict)


class StdResponse(BaseModel):
    """Normalized response for both LLM and OCR tasks.

    - `content` contains provider-agnostic output (text, structured object,
      or OCR text/blocks).
    - `raw` retains the provider-specific payload for debugging.
    - `error` is populated when `ok` is False.
    """

    ok: bool
    content: Any  # for LLM: text or structured object; for OCR: extracted text/blocks
    usage: Usage = Usage()
    raw: Dict[str, Any] = Field(default_factory=dict)  # provider payload (debug)
    error: Optional[str] = None


class BatchJob(BaseModel):
    """Metadata for batch executions.

    For `concurrent` mode, `result` is populated immediately with a list of
    `StdResponse`. For `native` provider batch APIs, `id` and `status` allow
    polling and later retrieval via provider-specific mechanisms.
    """

    id: str
    provider: str
    status: Literal[
        "queued", "running", "succeeded", "failed", "cancelled", "expired", "unknown"
    ] = "queued"
    # native batch may return output file handles/urls
    result: Optional[List[StdResponse]] = None  # populated for 'concurrent' mode
