"""Asynchronous summarizer with batching and rate limiting."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Mapping, Optional

from aiolimiter import AsyncLimiter
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from .summarizer import Summarizer, SummaryResult
from .model_router import RoutingDecision
from .usage import log_usage


@dataclass
class AsyncConfig:
    max_concurrent: int = 4
    requests_per_minute: int = 30
    max_attempts: int = 3


class AsyncSummarizer:
    def __init__(
        self,
        *,
        summarizer_factory,
        config: AsyncConfig,
    ) -> None:
        self.summarizer_factory = summarizer_factory
        self.config = config
        self.limiter = AsyncLimiter(config.requests_per_minute, time_period=60)

    async def summarise(self, decisions: Iterable[RoutingDecision]) -> List[SummaryResult]:
        results: List[SummaryResult] = []
        semaphore = asyncio.Semaphore(self.config.max_concurrent)

        async def run(decision: RoutingDecision) -> None:
            async with semaphore:
                async for attempt in AsyncRetrying(
                    stop=stop_after_attempt(self.config.max_attempts),
                    wait=wait_random_exponential(min=2, max=15),
                    retry=retry_if_exception_type(RuntimeError),
                ):
                    with attempt:
                        async with self.limiter:
                            summariser: Summarizer = self.summarizer_factory()
                            result = summariser.summarise([decision])[0]
                            results.append(result)

        await asyncio.gather(*(run(d) for d in decisions))
        return results
