import typer
import dotenv
import httpx
import json
import logging
import uuid

from enum import Enum

from slugkit import SyncClient
from slugkit.sync_client import RandomGenerator
from slugkit.base import StatsItem, SeriesInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.ERROR)

app = typer.Typer()


class OutputFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class AppContext:
    base_url: str
    api_key: str
    output_format: OutputFormat = OutputFormat.TEXT

    allow_extra_args: bool = False
    allow_interspersed_args: bool = False

    ignore_unknown_options: bool = False

    def __init__(self, base_url: str, api_key: str, output_format: OutputFormat):
        self.base_url = base_url
        self.api_key = api_key
        self.output_format = output_format


app_context = typer.Context(AppContext)


@app.callback()
def callback(
    *,
    base_url: str = typer.Option(
        ...,  # "https://dev.slugkit.dev/api/v1",
        envvar="SLUGKIT_BASE_URL",
        help="The base URL of the SlugKit API.",
    ),
    api_key: str = typer.Option(
        ...,
        envvar="SLUGKIT_API_KEY",
        help="The API key for the SlugKit API.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--output-format",
        "-o",
        help="The output format to use for the human-readable IDs.",
    ),
):
    """
    SlugKit Python SDK.
    """
    app_context.base_url = base_url
    app_context.api_key = api_key
    app_context.output_format = output_format


@app.command()
def forge(
    pattern: str = typer.Argument(..., help="The slug pattern to test."),
    *,
    seed: str | None = typer.Option(None, "--seed", "-s", help="The seed to use for the random number generator."),
    sequence: int | None = typer.Option(
        None, "--sequence", "-n", help="The sequence number to use for the random number generator."
    ),
    count: int = typer.Option(1, "--count", "-c", help="The number of human-readable IDs to generate."),
):
    """
    Get a list of slugs for a given pattern.
    """
    if seed is None:
        seed = str(uuid.uuid4())
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        result = client.forge(pattern, seed=seed, sequence=sequence, count=count)
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to test pattern: {e.response.text}")
        raise typer.Exit(1)
    if app_context.output_format == OutputFormat.JSON:
        print(json.dumps(result, indent=2))
    else:
        for slug in result:
            print(slug)


@app.command()
def mint(
    count: int = typer.Argument(1, help="The number of slugs to generate."),
    batch_size: int = typer.Option(1000, "--batch-size", "-b", help="Size of a batch to fetch at once."),
):
    """
    Generate next batch of slugs for the series defined by the API key.

    Generating slugs will bump the series counter. Slugs may be generated
    concurrently and will not collide.

    If the output format is JSON, the result will be a list of slugs.
    Otherwise, the result will be a stream of slugs.
    Default output format is text.
    """
    logger.info(f"Generating {count} human-readable IDs at {app_context.base_url}")
    client = SyncClient(app_context.base_url, app_context.api_key)
    gen = client.mint
    if count > 1:
        gen = gen.with_limit(count).with_batch_size(batch_size)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(list(gen), indent=2))
        else:
            for slug in gen:
                print(slug)
    elif count == 1:
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(gen(), indent=2))
        else:
            print(gen()[0])
    else:
        raise ValueError(f"Invalid count: {count}")


@app.command()
def slice(
    sequence: int = typer.Argument(0, help="The sequence number to start from."),
    count: int = typer.Argument(1, help="The number of slugs to generate."),
    batch_size: int = typer.Option(1000, "--batch-size", "-b", help="Size of a batch to fetch at once."),
):
    """
    Generate slugs starting from a given sequence number.
    Series counters are not bumped.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    gen = client.slice.starting_from(sequence)
    if count > 1:
        gen = gen.with_limit(count).with_batch_size(batch_size)
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(list(gen), indent=2))
        else:
            for slug in gen:
                print(slug)
    elif count == 1:
        if app_context.output_format == OutputFormat.JSON:
            print(json.dumps(gen(), indent=2))
        else:
            print(gen()[0])
    else:
        raise ValueError(f"Invalid count: {count}")


@app.command()
def stats():
    """
    Get the stats of the generator.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        stats_items = client.mint.stats()
        if app_context.output_format == OutputFormat.JSON:
            # Convert StatsItem objects to dictionaries for JSON serialization
            stats_dicts = [item.to_dict() for item in stats_items]
            print(json.dumps(stats_dicts, indent=2))
        else:
            caption_width = 25
            for item in stats_items:
                print(f"{'Event Type':<{caption_width}}: {item.event_type}")
                print(f"{'Date Part':<{caption_width}}: {item.date_part}")
                print(f"{'Total Count':<{caption_width}}: {item.total_count}")
                print(f"{'Request Count':<{caption_width}}: {item.request_count}")
                print(f"{'Total Duration (μs)':<{caption_width}}: {item.total_duration_us}")
                print(f"{'Avg Duration (μs)':<{caption_width}}: {item.avg_duration_us}")
                print("-" * 50)
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to get stats: {e.response.text}")
        raise typer.Exit(1)


@app.command()
def series_info():
    """
    Get information about the current series.
    """
    client = SyncClient(app_context.base_url, app_context.api_key)
    try:
        series_info = client.mint.series_info()
        if app_context.output_format == OutputFormat.JSON:
            # Convert SeriesInfo object to dictionary for JSON serialization
            series_dict = series_info.to_dict()
            print(json.dumps(series_dict, indent=2))
        else:
            caption_width = 25
            print(f"{'Series Slug':<{caption_width}}: {series_info.slug}")
            print(f"{'Organization Slug':<{caption_width}}: {series_info.org_slug}")
            print(f"{'Pattern':<{caption_width}}: {series_info.pattern}")
            print(f"{'Max Pattern Length':<{caption_width}}: {series_info.max_pattern_length}")
            print(f"{'Capacity':<{caption_width}}: {series_info.capacity}")
            print(f"{'Generated Count':<{caption_width}}: {series_info.generated_count}")
            print(f"{'Last Modified':<{caption_width}}: {series_info.mtime}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to get series info: {e.response.text}")
        raise typer.Exit(1)


@app.command()
def reset():
    """
    Reset the generator.
    """
    try:
        logger.warning(f"Resetting generator at {app_context.base_url}")
        client = SyncClient(app_context.base_url, app_context.api_key)
        client.mint.reset()
        logger.info("Generator reset")
    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to reset generator: {e.response.text}")
        raise typer.Exit(1)


def main():
    dotenv.load_dotenv()
    app()


if __name__ == "__main__":
    main()
