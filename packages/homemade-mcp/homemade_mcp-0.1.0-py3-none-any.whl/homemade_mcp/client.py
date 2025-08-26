# -*- coding: utf-8 -*-
# src/homemade_mcp/client.py
"""Client for unified LLM/OCR requests across multiple providers.

This module exposes the `LLMClient`, the single entry point for running
standardized requests against different providers (OpenAI, Gemini, Mistral OCR)
using a unified schema defined in `schemas.py`.
"""

from typing import Dict, List

from homemade_mcp.adapters.gemini_adapter import GeminiAdapter
from homemade_mcp.adapters.mistral_ocr_adapter import MistralOCRAdapter
from homemade_mcp.adapters.openai_adapter import OpenAIAdapter
from homemade_mcp.schemas import BatchJob, StdRequest, StdResponse


class LLMClient:
    """Dispatch requests to provider adapters using a unified schema.

    The client wires provider credentials to their corresponding adapters and
    exposes two public methods:
    - `run` executes a single `StdRequest` and returns a `StdResponse`.
    - `run_batch` executes multiple homogeneous-provider requests either via
      async fan-out (``mode="concurrent"``) or a provider's native batch API
      (``mode="native"``) when available.
    """

    def __init__(self, creds: Dict[str, Dict[str, str]]):
        """Initialize the client with provider credentials.

        Args:
            creds: Mapping from provider name to credentials, e.g.::

                {
                  "openai": {"api_key": "..."},
                  "gemini": {"api_key": "..."},
                  "mistral_ocr": {"api_key": "..."}
                }

        Only providers present in this mapping are enabled.
        """
        self.adapters = {}
        if "openai" in creds:
            self.adapters["openai"] = OpenAIAdapter(**creds["openai"])
        if "gemini" in creds:
            self.adapters["gemini"] = GeminiAdapter(**creds["gemini"])
        if "mistral_ocr" in creds:
            self.adapters["mistral_ocr"] = MistralOCRAdapter(**creds["mistral_ocr"])

    async def run(self, req: StdRequest) -> StdResponse:
        """Execute a single standardized request.

        Args:
            req: The standardized request (provider, model, task, input).

        Returns:
            A normalized `StdResponse` with provider raw payload in `raw`.
        """
        return await self.adapters[req.provider].run(req)

    async def run_batch(
        self, reqs: List[StdRequest], mode: str = "concurrent"
    ) -> BatchJob:
        """Execute a batch of requests from the same provider.

        Args:
            reqs: List of requests. All must target the same provider.
            mode: "concurrent" for async fan-out, or "native" to use the
                provider's batch API if implemented.

        Returns:
            A `BatchJob` describing the job and results for concurrent mode.

        Raises:
            AssertionError: If the list is empty or providers are mixed.
        """
        assert reqs, "empty batch"
        provider = reqs[0].provider
        assert all(r.provider == provider for r in reqs), (
            "mixed providers not supported in one job"
        )
        return await self.adapters[provider].run_batch(reqs, mode=mode)
