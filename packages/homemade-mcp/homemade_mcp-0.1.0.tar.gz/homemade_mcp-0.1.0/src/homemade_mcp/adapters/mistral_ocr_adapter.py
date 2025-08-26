# -*- coding: utf-8 -*-
# src/homemade_mcp/adapters/mistral_ocr_adapter.py
"""Adapter for Mistral OCR.

Minimal v1 adapter that posts a URL/path to a hypothetical OCR endpoint and
normalizes the output into `StdResponse`. Starts with concurrent batching; a
native batch mode can be added when the provider supports it.
"""

import asyncio
import uuid
from typing import List

import httpx

from homemade_mcp.schemas import BatchJob, StdRequest, StdResponse


class MistralOCRAdapter:
    """Mistral OCR adapter implementing the common adapter contract."""

    def __init__(self, api_key: str, base_url: str = "https://api.mistral.ai"):
        self.api_key = api_key
        self.base_url = base_url

    async def run(self, req: StdRequest) -> StdResponse:
        """Execute a single OCR request and normalize the response."""
        # Very simple: send URL to OCR endpoint; adapt to official payload once you pick it
        payload = {"model": req.model, "input": {"source": req.input.source}}
        if getattr(req.input, "pages", None):
            payload["input"]["pages"] = list(
                req.input.pages
            )  # pass-through optional pages
        async with httpx.AsyncClient(timeout=120) as http:
            r = await http.post(
                f"{self.base_url}/v1/ocr",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if r.status_code >= 400:
            return StdResponse(ok=False, content=None, raw=r.json(), error=r.text)
        data = r.json()
        # Normalize to a single text field for v1
        text = data.get("text") or data
        return StdResponse(ok=True, content=text, raw=data)

    async def run_batch(
        self,
        reqs: List[StdRequest],
        mode: str = "concurrent",
    ) -> BatchJob:
        """Execute a batch via concurrent fan-out.

        The `mode` parameter is accepted for signature compatibility with other
        adapters; only "concurrent" is supported at present.
        """
        # Start with concurrent fan-out; you can add a native batch if Mistral exposes one later

        async def one(r: StdRequest) -> StdResponse:
            return await self.run(r)

        rs = await asyncio.gather(*[one(x) for x in reqs], return_exceptions=True)

        norm = [
            x if isinstance(x, StdResponse) else StdResponse(ok=False, error=str(x))
            for x in rs
        ]

        return BatchJob(
            id=str(uuid.uuid4()),
            provider="mistral_ocr",
            status="succeeded",
            result=norm,
        )
