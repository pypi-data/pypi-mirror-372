from __future__ import annotations

import asyncio
from typing import Any, cast

import httpx
from loguru import logger

from calllogdb.core import Config


class AsyncAPIClient:
    def __init__(self, config: Config, max_retries: int = 3, timeout: float = 60.0) -> None:
        self.url: str = config.url or ""
        self.token: str = config.token or ""
        self.max_retries: int = max_retries
        self.client = httpx.AsyncClient(
            base_url=self.url,
            headers={
                "Accept": "application/json",
                "Authorization": self.token,
            },
            timeout=timeout,
            follow_redirects=True,
        )

    async def get(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(1, self.max_retries + 1):
            try:
                resp: httpx.Response = await self.client.get(self.url, params=params)
                resp.raise_for_status()
                return cast(dict[str, Any], resp.json())

            except httpx.ReadError as e:
                logger.warning("Попытка %d/%d — ReadError: %s", attempt, self.max_retries, e)
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(2)

            except httpx.TimeoutException:
                logger.error("Таймаут при запросе к {}", self.url)
                return {}

            except httpx.HTTPStatusError as e:
                logger.error("Ошибка HTTP: %s", e)
                if e.response.status_code in {500, 502, 503, 504}:
                    return {}
                raise

            except httpx.HTTPError as e:
                logger.error("Ошибка сети: %s", e)
                raise

        return {}

    async def __aenter__(self) -> "AsyncAPIClient":
        logger.debug("AsyncAPIClient __aenter__")
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.client.aclose()
