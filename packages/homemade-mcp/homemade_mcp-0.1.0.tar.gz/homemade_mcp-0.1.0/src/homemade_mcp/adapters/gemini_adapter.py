# -*- coding: utf-8 -*-
# src/homemade_mcp/adapters/gemini_adapter.py
"""Adapter for Google Gemini models.

Maps the unified `StdRequest` into Gemini SDK calls and normalizes outputs
to `StdResponse`. Supports structured outputs, thinking budget, and optional
Google Search grounding.
"""

import asyncio
import base64
import uuid
from typing import List

from google import genai
from google.genai import types

from homemade_mcp.adapters.utils import to_internal_message
from homemade_mcp.schemas import BatchJob, StdRequest, StdResponse


def _to_gemini_contents(req: StdRequest) -> List[types.Content]:
    """Translate internal message parts into Gemini `Content` objects."""
    imsg = to_internal_message(req.input.blocks)
    parts = []
    for p in imsg["content"]:
        if p["type"] == "text":
            parts.append(types.Part.from_text(text=p["text"]))
        else:
            parts.append(
                types.Part.from_bytes(
                    mime_type="image/png",
                    data=base64.b64decode(p["image"]["b64"]),  # type: ignore[arg-type]
                )
            )
    return [types.Content(role="user", parts=parts)]


class GeminiAdapter:
    """Google Gemini adapter implementing the common adapter contract."""

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def _to_config(self, req: StdRequest):
        """Build Gemini generation config from a `StdRequest`."""
        tools = []
        if isinstance(req.input, dict):
            pass
        if getattr(req.input, "search", False):
            tools.append(types.Tool(google_search=types.GoogleSearch()))
        cfg = types.GenerateContentConfig(tools=tools)
        # structured output
        if req.input.json_schema:
            cfg.response_mime_type = "application/json"
            cfg.response_schema = types.Schema.from_json_schema(
                json_schema=req.input.json_schema, api_option="GEMINI_API"
            )
        # thinking
        think = req.input.thinking
        if think and think != "off":
            # simple mapping; you can refine
            budget = {"low": 2048, "medium": 8192, "high": 32768, "auto": -1}.get(
                think, 0
            )
            cfg.thinking = types.ThinkingConfig(
                thinking_budget=budget
            )  # or .thinkingBudget depending on SDK
        # misc params
        for k, v in (req.input.params or {}).items():
            setattr(cfg, k, v)
        return cfg

    async def run(self, req: StdRequest) -> StdResponse:
        """Execute a single request against Gemini and normalize the response."""
        contents = _to_gemini_contents(req)
        cfg = self._to_config(req)
        r = self.client.models.generate_content(
            model=req.model, contents=contents, config=cfg
        )
        # normalize
        content = (
            getattr(r, "text", None) or r.candidates[0].content.parts[0].text
            if r.candidates
            else r
        )
        return StdResponse(
            ok=True, content=content, raw=r.to_dict() if hasattr(r, "to_dict") else r
        )

    async def run_batch(
        self, reqs: List[StdRequest], mode: str = "concurrent"
    ) -> BatchJob:
        """Execute a batch via concurrent fan-out or Gemini batch API."""
        if mode == "concurrent":

            async def one(req: StdRequest) -> StdResponse:
                return await self.run(req)

            results = await asyncio.gather(
                *[one(r) for r in reqs], return_exceptions=True
            )
            norm = [
                r if isinstance(r, StdResponse) else StdResponse(ok=False, error=str(r))
                for r in results
            ]
            return BatchJob(
                id=str(uuid.uuid4()), provider="gemini", status="succeeded", result=norm
            )

        # native Batch Mode: inline for small lists (SDK supports it)
        # Note: we convert to contents directly; messages isn't used in this codebase
        inline_requests = [{"contents": _to_gemini_contents(r)} for r in reqs]
        job = self.client.batches.create(
            model=reqs[0].model,
            src=inline_requests,
            config={"display_name": "unillm-batch"},
        )
        return BatchJob(id=job.name, provider="gemini", status="queued")
