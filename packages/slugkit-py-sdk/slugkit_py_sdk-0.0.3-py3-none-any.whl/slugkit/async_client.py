import httpx
import os

from typing import Any, Self, AsyncGenerator, Callable

from .base import GeneratorBase, StatsItem, SeriesInfo


class AsyncSlugGenerator(GeneratorBase):
    async def __call__(self, count: int = 1) -> list[str]:
        req = self._get_request(count)
        path = self._get_path()
        client = await self._http_client()
        response = await client.post(path, json=req)
        response.raise_for_status()
        return response.json()

    async def mint(self) -> AsyncGenerator[str, Any]:
        count = 0
        limit = self._limit
        batch_size = self._batch_size
        sequence = self._sequence
        path = self._get_path(stream=True)

        try:
            while True:
                if limit is not None and count >= limit:
                    break

                current_batch_size = min(batch_size, limit - count) if limit is not None else batch_size
                if current_batch_size <= 0:
                    break

                client = await self._http_client()
                async with client:
                    if not self._dry_run:
                        req = {"count": current_batch_size}
                    else:
                        req = {"count": current_batch_size, "sequence": sequence}

                    # Get the streaming response and use it as a context manager
                    stream_response = await client.stream(
                        "POST",
                        path,
                        json=req,
                    )
                    async with stream_response as response:
                        response.raise_for_status()
                        # Get the async iterator and use it
                        async_lines = await response.aiter_lines()
                        async for val in async_lines:
                            yield val.strip()
                            count += 1
                            if limit is not None and count >= limit:
                                return
                sequence += current_batch_size
        except Exception as e:
            # Log error and break to avoid infinite loops
            import logging

            logging.error(f"Error in async mint: {e}")
            return

    async def reset(self) -> None:
        client = await self._http_client()
        response = await client.post(self.RESET_PATH)
        response.raise_for_status()

    async def stats(self) -> list[StatsItem]:
        client = await self._http_client()
        response = await client.get(self.STATS_PATH)
        response.raise_for_status()
        data = response.json()
        return [StatsItem.from_dict(item) for item in data]

    async def series_info(self) -> SeriesInfo:
        client = await self._http_client()
        response = await client.get(self.SERIES_INFO_PATH)
        response.raise_for_status()
        data = response.json()
        return SeriesInfo.from_dict(data)

    async def __aiter__(self) -> AsyncGenerator[str, None]:
        return self.mint()


class AsyncRandomGenerator(GeneratorBase):
    def __init__(self, http_client: Callable[[], httpx.AsyncClient]):
        self._http_client = http_client

    async def __call__(
        self,
        pattern: str,
        *,
        seed: str | None = None,
        sequence: int | None = None,
        count: int = 1,
    ) -> list[str]:
        req = {
            "pattern": pattern,
        }
        if seed:
            req["seed"] = seed
        if sequence:
            req["sequence"] = sequence
        if count:
            req["count"] = count
        client = await self._http_client()
        response = await client.post(self.FORGE_PATH, json=req)
        response.raise_for_status()
        return response.json()


class AsyncClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        httpx_client_factory: Callable[[], Any] = httpx.AsyncClient,
        timeout: float = 10.0,
    ):
        if not base_url:
            base_url = os.getenv("SLUGKIT_BASE_URL")
        if not base_url:
            raise ValueError("SLUGKIT_BASE_URL is not set")
        if not api_key:
            api_key = os.getenv("SLUGKIT_API_KEY")
        self.base_url = base_url
        self._api_key = api_key
        self._httpx_client_factory = httpx_client_factory
        self._timeout = timeout

    @property
    def api_key(self) -> str | None:
        """Get the API key."""
        return self._api_key

    async def _http_client(self) -> httpx.AsyncClient:
        return self._httpx_client_factory(
            base_url=self.base_url,
            headers={"x-api-key": self._api_key},
            timeout=self._timeout,
        )

    @property
    def mint(self) -> AsyncSlugGenerator:
        if not self._api_key:
            raise ValueError("Mint API is available only for authenticated series")
        return AsyncSlugGenerator(self._http_client)

    def __getitem__(self, series_slug: str) -> AsyncSlugGenerator:
        return self.mint.with_series(series_slug)

    @property
    def slice(self) -> AsyncSlugGenerator:
        if not self._api_key:
            raise ValueError("Slice API is available only for authenticated series")
        return AsyncSlugGenerator(self._http_client).with_dry_run()

    @property
    def forge(self) -> AsyncRandomGenerator:
        if not self._api_key:
            raise ValueError("Forge API is available only for authenticated series")
        return AsyncRandomGenerator(self._http_client)
