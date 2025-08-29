import httpx
from enum import Enum
from typing import Any, Callable, Self


class EventType(Enum):
    """Enum for event types in stats responses."""

    FORGE = "forge"
    MINT = "mint"
    SLICE = "slice"
    RESET = "reset"


class DatePart(Enum):
    """Enum for date parts in stats responses."""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    TOTAL = "total"


class StatsItem:
    """Class representing a single stats item from the API response."""

    def __init__(
        self,
        event_type: str,
        date_part: str,
        total_count: int,
        request_count: int,
        total_duration_us: int,
        avg_duration_us: float,
    ):
        self.event_type = event_type
        self.date_part = date_part
        self.total_count = total_count
        self.request_count = request_count
        self.total_duration_us = total_duration_us
        self.avg_duration_us = avg_duration_us

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StatsItem":
        """Create a StatsItem instance from a dictionary."""
        return cls(
            event_type=data["event_type"],
            date_part=data["date_part"],
            total_count=data["total_count"],
            request_count=data["request_count"],
            total_duration_us=data["total_duration_us"],
            avg_duration_us=data["avg_duration_us"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the StatsItem to a dictionary."""
        return {
            "event_type": self.event_type,
            "date_part": self.date_part,
            "total_count": self.total_count,
            "request_count": self.request_count,
            "total_duration_us": self.total_duration_us,
            "avg_duration_us": self.avg_duration_us,
        }

    def __repr__(self) -> str:
        return (
            f"StatsItem(event_type='{self.event_type}', date_part='{self.date_part}', total_count={self.total_count})"
        )


class SeriesInfo:
    """Class representing series information from the API response."""

    def __init__(
        self,
        slug: str,
        org_slug: str,
        pattern: str,
        max_pattern_length: int,
        capacity: str,
        generated_count: str,
        mtime: str,
    ):
        self.slug = slug
        self.org_slug = org_slug
        self.pattern = pattern
        self.max_pattern_length = max_pattern_length
        self.capacity = capacity
        self.generated_count = generated_count
        self.mtime = mtime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SeriesInfo":
        """Create a SeriesInfo instance from a dictionary."""
        return cls(
            slug=data["slug"],
            org_slug=data["org_slug"],
            pattern=data["pattern"],
            max_pattern_length=data["max_pattern_length"],
            capacity=data["capacity"],
            generated_count=data["generated_count"],
            mtime=data["mtime"],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the SeriesInfo to a dictionary."""
        return {
            "slug": self.slug,
            "org_slug": self.org_slug,
            "pattern": self.pattern,
            "max_pattern_length": self.max_pattern_length,
            "capacity": self.capacity,
            "generated_count": self.generated_count,
            "mtime": self.mtime,
        }

    def __repr__(self) -> str:
        return f"SeriesInfo(slug='{self.slug}', pattern='{self.pattern}', capacity={self.capacity})"


class GeneratorBase:
    MINT_PATH = "/gen/mint"
    SLICE_PATH = "/gen/slice"
    FORGE_PATH = "/gen/forge"
    RESET_PATH = "/gen/reset"
    STATS_PATH = "/gen/stats/latest"
    SERIES_INFO_PATH = "/gen/series-info"

    def __init__(
        self,
        http_client: Callable[[], httpx.Client],
        *,
        series_slug: str | None = None,
        batch_size: int = 1000,
        limit: int | None = None,
        dry_run: bool = False,
        sequence: int = 0,
    ):
        self._http_client = http_client
        self._series_slug = series_slug
        self._batch_size = batch_size
        self._limit = limit
        self._dry_run = dry_run
        self._sequence = sequence

    def with_series(self, series_slug: str) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_batch_size(self, batch_size: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_limit(self, limit: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=limit,
            dry_run=self._dry_run,
            sequence=self._sequence,
        )

    def with_dry_run(self) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=True,
            sequence=self._sequence,
        )

    def starting_from(self, sequence: int) -> Self:
        return self.__class__(
            self._http_client,
            series_slug=self._series_slug,
            batch_size=self._batch_size,
            limit=self._limit,
            dry_run=self._dry_run,
            sequence=sequence,
        )

    def _get_request(self, count: int, sequence: int | None = None) -> dict[str, Any]:
        req = {"count": count}
        if self._dry_run and sequence is not None:
            req["sequence"] = sequence
        if self._series_slug:
            req["series"] = self._series_slug
        return req

    def _get_path(self, stream: bool = False) -> str:
        path = self.MINT_PATH
        if self._dry_run:
            path = self.SLICE_PATH
        if stream:
            path = f"{path}/stream"
        return path
