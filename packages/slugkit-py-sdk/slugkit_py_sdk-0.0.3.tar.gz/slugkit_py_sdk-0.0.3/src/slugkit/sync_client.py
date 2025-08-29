import httpx
import os
import logging
import functools

from typing import Any, Self, Generator, Callable
from .base import GeneratorBase, StatsItem, SeriesInfo

logger = logging.getLogger(__name__)


class SyncSlugGenerator(GeneratorBase):
    def __call__(
        self,
        count: int = 1,
    ) -> list[str]:
        req = self._get_request(count)
        path = self._get_path()

        response = self._http_client().post(
            path,
            json=req,
        )
        response.raise_for_status()
        return response.json()

    def mint(self) -> Generator[str, Any, int]:
        count = 0
        limit = self._limit
        batch_size = self._batch_size
        path = self._get_path(stream=True)
        sequence = self._sequence
        try:
            while True:
                if limit is not None:
                    batch_size = min(batch_size, limit - count)
                if batch_size <= 0:
                    break
                with self._http_client() as client:
                    req = self._get_request(batch_size, sequence)
                    logger.info(f"Requesting batch of {batch_size} slugs")
                    with client.stream(
                        "POST",
                        path,
                        json=req,
                    ) as response:
                        response.raise_for_status()

                        for val in response.iter_lines():
                            stop = yield val.strip()
                            count += 1
                            if stop is not None:
                                break
                            if limit is not None and count >= limit:
                                break
                sequence += batch_size
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                e.response.read()
                logger.error(f"Error: {e.response.text}")
                raise Exception(f"Error: {e.response.text}")
            raise
        except KeyboardInterrupt:
            return count
        return count

    def reset(self) -> None:
        response = self._http_client().post(self.RESET_PATH)
        response.raise_for_status()

    def stats(self) -> list[StatsItem]:
        response = self._http_client().get(self.STATS_PATH)
        response.raise_for_status()
        data = response.json()
        return [StatsItem.from_dict(item) for item in data]

    def series_info(self) -> SeriesInfo:
        response = self._http_client().get(self.SERIES_INFO_PATH)
        response.raise_for_status()
        data = response.json()
        return SeriesInfo.from_dict(data)

    def __iter__(self) -> Generator[str, None, None]:
        return self.mint()


class RandomGenerator(GeneratorBase):
    def __init__(self, http_client: Callable[[], httpx.Client]):
        self._http_client = http_client

    def __call__(
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
        response = self._http_client().post(
            self.FORGE_PATH,
            json=req,
        )
        response.raise_for_status()
        return response.json()


class SyncClient:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        *,
        httpx_client_factory: Callable[[], Any] = httpx.Client,
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

    def _http_client(self) -> httpx.Client:
        return self._httpx_client_factory(
            base_url=self.base_url,
            headers={"x-api-key": self._api_key},
            timeout=self._timeout,
        )

    @functools.cached_property
    def mint(self) -> SyncSlugGenerator:
        if not self._api_key:
            raise ValueError("Mint API is available only for authenticated series")
        return SyncSlugGenerator(self._http_client)

    def __getitem__(self, series_slug: str) -> SyncSlugGenerator:
        return self.mint.with_series(series_slug)

    @functools.cached_property
    def slice(self) -> SyncSlugGenerator:

        if not self._api_key:
            raise ValueError("Mint API is available only for authenticated series")
        return SyncSlugGenerator(self._http_client).with_dry_run()

    @functools.cached_property
    def forge(self) -> RandomGenerator:
        if not self._api_key:
            raise ValueError("Forge API is available only for authenticated series")
        return RandomGenerator(self._http_client)
