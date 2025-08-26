# -*- coding: utf-8 -*-
# src/homemade_mcp/adapters/base.py
"""Abstract base class for provider adapters.

Every provider implementation should subclass this contract and implement the
`run` and `run_batch` coroutines with consistent semantics.
"""

from abc import ABC, abstractmethod
from typing import List

from homemade_mcp.schemas import BatchJob, StdRequest, StdResponse


class BaseAdapter(ABC):
    """Common adapter interface for providers."""

    def __init__(self, api_key: str, **kwargs):
        """Store API key and any provider-specific kwargs."""
        self.api_key = api_key
        self.kwargs = kwargs

    @abstractmethod
    async def run(self, req: StdRequest) -> StdResponse:
        """Execute a single standardized request and return a normalized response."""

    # mode = "native" (provider batch API) or "concurrent" (async fan-out)
    @abstractmethod
    async def run_batch(
        self, reqs: List[StdRequest], mode: str = "concurrent"
    ) -> BatchJob:
        """Execute a batch of requests using either concurrent or native mode."""
