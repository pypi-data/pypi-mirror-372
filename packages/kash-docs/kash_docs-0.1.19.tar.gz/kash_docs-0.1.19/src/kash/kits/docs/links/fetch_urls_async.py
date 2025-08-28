from __future__ import annotations

import asyncio
from typing import Any

from strif import abbrev_str

from kash.config.logger import get_logger
from kash.exec.fetch_url_items import fetch_url_item
from kash.kits.docs.actions.text.markdownify_doc import markdownify_doc
from kash.kits.docs.links.links_model import FetchError, FetchStatus, Link, LinkDownloadResult
from kash.utils.api_utils.api_retries import RetrySettings
from kash.utils.api_utils.gather_limited import FuncTask, Limit, TaskResult
from kash.utils.api_utils.http_utils import extract_http_status_code
from kash.utils.api_utils.multitask_gather import multitask_gather
from kash.utils.common.url import Url
from kash.utils.text_handling.markdown_utils import extract_urls

log = get_logger(__name__)


class HTTPClientError(Exception):
    """
    Clean exception wrapper for HTTP client errors to avoid verbose stack traces.
    """

    status_code: int
    url: str

    def __init__(self, status_code: int, url: str):
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code} for URL: {self.url}")


def fetch_url_task(
    url: Url, *, save_content: bool = True, refetch: bool = False, convert_to_md: bool = True
) -> TaskResult[Link]:
    """
    Download a single URL and extract metadata, by default also saving to cache.
    Returns TaskResult with disable_limits=True for cached content to bypass rate limiting.
    Returns Link with appropriate status and status_code populated.
    """

    try:
        fetch_result = fetch_url_item(
            url, save_content=save_content, refetch=refetch, cache=True, overwrite=True
        )

        orig_item = fetch_result.item
        if orig_item.format and (
            orig_item.format.is_markdown or orig_item.format.is_markdown_with_html
        ):
            md_item = orig_item
        elif convert_to_md:
            md_item = markdownify_doc(orig_item)
        else:
            md_item = None

        # Successful fetch
        status_code = 200
        link = Link(
            url=url,
            title=fetch_result.item.title,
            description=fetch_result.item.description,
            status=FetchStatus.from_status_code(status_code),
            status_code=status_code,
            content_orig_path=orig_item.store_path,
            content_md_path=(md_item and md_item.store_path) or orig_item.store_path,
        )

        # If content was cached, bypass rate limiting since no actual network request was made
        if fetch_result.was_cached:
            log.debug("Using cached content for %s (bypassing rate limits)", url)
            return TaskResult(link, disable_limits=True)

        # Content was fetched from network, apply normal rate limiting
        return TaskResult(link, disable_limits=False)

    except Exception as e:
        # Extract HTTP status code if available
        status_code = extract_http_status_code(e)

        # Determine appropriate status using class method
        status = (
            FetchStatus.from_status_code(status_code) if status_code else FetchStatus.fetch_error
        )

        # Create Link object with error status instead of raising exception
        error_link = Link(
            url=url,
            title=None,
            description=None,
            status=status,
            status_code=status_code,
        )

        return TaskResult(error_link, disable_limits=False)


def bucket_for(url: Url) -> str:
    from urllib.parse import urlparse

    parsed = urlparse(str(url))
    return parsed.hostname or "unknown"


OVERALL_LIMIT = Limit(rps=20, concurrency=20)
PER_HOST_LIMIT = Limit(rps=2, concurrency=2)


# Custom retry settings for link fetching
LINK_FETCH_RETRIES = RetrySettings(
    max_task_retries=3,
    max_total_retries=50,
    initial_backoff=1.0,
    max_backoff=60.0,
    backoff_factor=2.0,
)


async def fetch_urls_async(urls: list[Url], show_progress: bool = True) -> LinkDownloadResult:
    """
    Download a list of URLs and return both successful results and errors.
    Uses cache-aware rate limiting; cached content bypasses rate limits for faster processing.
    """
    if not urls:
        log.message("No URLs to download")
        return LinkDownloadResult(links=[], errors=[])

    log.message("Downloading %d links...", len(urls))

    download_tasks: list[FuncTask[Link]] = [
        FuncTask(fetch_url_task, (url,), bucket=bucket_for(url)) for url in urls
    ]

    def labeler(i: int, spec: Any) -> str:
        if isinstance(spec, FuncTask) and len(spec.args) >= 1:
            url = spec.args[0]
            return f"Link {i + 1}/{len(urls)}: {abbrev_str(url, 50)}"
        return f"Link {i + 1}/{len(urls)}"

    log.message(
        "Rate limits: overall %s, per host %s (cached content bypasses limits)",
        OVERALL_LIMIT,
        PER_HOST_LIMIT,
    )
    gather_result = await multitask_gather(
        download_tasks,
        labeler=labeler,
        limit=OVERALL_LIMIT,
        bucket_limits={"*": PER_HOST_LIMIT},
        retry_settings=LINK_FETCH_RETRIES,
    )
    if len(gather_result.successes) == 0:
        raise RuntimeError("fetch_urls_async: no successful downloads")

    task_results: list[Link] = gather_result.successes

    links: list[Link] = []
    errors: list[FetchError] = []

    for link in task_results:
        assert isinstance(link, Link)
        if link.status.is_error:
            errors.append(
                FetchError(
                    url=link.url,
                    error_message=f"Status: {link.status_code} ({link.status.value})",
                )
            )
            log.warning(
                "Failed to fetch URL %s: Status %s (%s)",
                link.url,
                link.status_code,
                link.status.value,
            )

        links.append(link)

    return LinkDownloadResult(links=links, errors=errors)


## Tests


def test_fetch_links_with_mock_links():
    """Test the link extraction part without actually downloading URLs."""
    from textwrap import dedent

    markdown_content = dedent("""
        # Test Document
        
        Check out [GitHub](https://github.com) for code repositories.
        
        You can also visit [Python.org](https://python.org) for documentation.
        """).strip()

    links = extract_urls(markdown_content, include_internal=False)
    assert len(links) == 2
    assert "https://github.com" in links
    assert "https://python.org" in links


def test_fetch_urls_async_empty_behavior():
    """Test fetch_urls_async handles empty input correctly."""
    result = asyncio.run(fetch_urls_async([]))
    assert len(result.links) == 0
    assert len(result.errors) == 0
    assert result.total_errors == 0
    assert result.total_successes == 0
