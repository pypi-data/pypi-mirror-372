# -*- coding: utf-8 -*-
# src/homemade_mcp/adapters/openai_adapter.py
"""Adapter for OpenAI responses API.

Translates the unified `StdRequest` into the OpenAI `/responses` endpoint and
normalizes outputs to `StdResponse`. Supports structured outputs via
`response_format` and reasoning effort when available on the target model.
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List

import httpx

from homemade_mcp.adapters.utils import to_internal_message
from homemade_mcp.schemas import BatchJob, StdRequest, StdResponse

OPENAI_BASE = "https://api.openai.com/v1"


def _openai_headers(api_key: str):
    """Return standard OpenAI HTTP headers."""
    return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


def _map_openai_parts(internal_msg: Dict[str, Any]) -> Dict[str, Any]:
    """Map internal message parts to OpenAI `content` array format."""

    def map_part(p):
        if p["type"] == "text":
            return {"type": "text", "text": p["text"]}
        # use data URL for images (keeps it simple)
        data_url = f"data:image/png;base64,{p['image']['b64']}"
        return {"type": "image_url", "image_url": {"url": data_url}}

    return {
        "role": internal_msg["role"],
        "content": [map_part(p) for p in internal_msg["content"]],
    }


def _to_openai_responses_body(req: StdRequest) -> dict:
    """Build request body for OpenAI `/responses` from a `StdRequest`."""
    user_msg = _map_openai_parts(to_internal_message(req.input.blocks))
    body = {"model": req.model, "input": [user_msg]}
    if req.input.json_schema:
        body["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "schema", "schema": req.input.json_schema},
        }
    if req.input.thinking and req.input.thinking != "off":
        body["reasoning"] = {"effort": req.input.thinking}
    body.update(req.input.params or {})
    return body


class OpenAIAdapter:
    """OpenAI adapter implementing the common adapter contract."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def run(self, req: StdRequest) -> StdResponse:
        """Execute a single request against OpenAI and normalize the response."""
        body = _to_openai_responses_body(req)
        async with httpx.AsyncClient(timeout=60) as http:
            r = await http.post(
                f"{OPENAI_BASE}/responses",
                headers=_openai_headers(self.api_key),
                json=body,
            )
        if r.status_code >= 400:
            return StdResponse(ok=False, content=None, raw=r.json(), error=r.text)
        data = r.json()
        # normalize: prefer text or parsed JSON (if structured outputs)
        out = data.get("output") or data.get("choices") or data
        return StdResponse(ok=True, content=out, raw=data)

    async def run_batch(
        self, reqs: List[StdRequest], mode: str = "concurrent"
    ) -> BatchJob:
        """Execute a batch via concurrent fan-out or OpenAI batch JSONL API."""
        if mode == "concurrent":
            async with httpx.AsyncClient(timeout=60) as http:
                tasks = [
                    http.post(
                        f"{OPENAI_BASE}/responses",
                        headers=_openai_headers(self.api_key),
                        json=_to_openai_responses_body(r),
                    )
                    for r in reqs
                ]
                rs = await asyncio.gather(*tasks, return_exceptions=True)
            results = []
            for r in rs:
                if isinstance(r, BaseException):
                    results.append(StdResponse(ok=False, content=None, error=str(r)))
                elif r.status_code >= 400:
                    results.append(
                        StdResponse(ok=False, content=None, raw=r.json(), error=r.text)
                    )
                else:
                    data = r.json() or r
                    results.append(StdResponse(ok=True, content=data, raw=data))
            return BatchJob(
                id=str(uuid.uuid4()),
                provider="openai",
                status="succeeded",
                result=results,
            )

        # native batch (jsonl upload): cheaper, async; you poll for results later
        tasks = []
        for i, r in enumerate(reqs):
            tasks.append(
                {
                    "custom_id": f"task-{i}",
                    "method": "POST",
                    "url": "/v1/responses",
                    "body": _to_openai_responses_body(r),
                }
            )
        jsonl = "\n".join(json.dumps(t) for t in tasks)
        async with httpx.AsyncClient(timeout=60) as http:
            f = await http.post(
                f"{OPENAI_BASE}/files",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": ("batch.jsonl", jsonl), "purpose": (None, "batch")},
            )
            file_id = f.json()["id"]
            b = await http.post(
                f"{OPENAI_BASE}/batches",
                headers=_openai_headers(self.api_key),
                json={
                    "input_file_id": file_id,
                    "endpoint": "/v1/responses",
                    "completion_window": "24h",
                },
            )
        job = b.json()
        return BatchJob(id=job["id"], provider="openai", status="queued")
