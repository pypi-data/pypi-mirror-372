from __future__ import annotations

import asyncio

from frontmatter_format import to_yaml_string
from prettyfmt import fmt_lines

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import has_html_body, has_markdown_body, has_markdown_with_html_body
from kash.kits.docs.actions.text.extract_doc_links import extract_doc_links
from kash.kits.docs.links.fetch_urls_async import fetch_urls_async
from kash.kits.docs.links.links_model import LinkResults
from kash.kits.docs.links.links_preconditions import is_links_data
from kash.kits.docs.links.links_utils import parse_links_results_item
from kash.model import Format, Item, Param, TitleTemplate
from kash.utils.common.url import Url
from kash.utils.errors import InvalidInput

log = get_logger(__name__)


@kash_action(
    precondition=has_markdown_body | has_markdown_with_html_body | has_html_body | is_links_data,
    output_format=Format.yaml,
    title_template=TitleTemplate("Link metadata from {title}"),
    live_output=True,
    params=(
        Param(
            name="refetch",
            description="Whether to refetch links that have already been fetched.",
            type=bool,
        ),
    ),
)
def fetch_links(item: Item, refetch: bool = False) -> Item:
    """
    Download metadata for links from either markdown content or a links data item.
    If the input is markdown, extracts links first then downloads metadata.
    If the input is already a links data item, downloads metadata for those links.
    Uses cache-aware rate limiting for faster processing of cached content.
    Returns a YAML data item with URL, title, and description for each link.
    """
    # If input is markdown, first extract the links
    if has_markdown_body(item) or has_markdown_with_html_body(item) or has_html_body(item):
        links_item = extract_doc_links(item)
    elif is_links_data(item):
        links_item = item
    else:
        raise InvalidInput(f"Item must have markdown body or links data: {item}")

    links_data = parse_links_results_item(links_item)
    # Don't fetch links that are already fetched or have permanent errors.
    urls = [Url(link.url) for link in links_data.links if refetch or link.status.should_fetch]

    if not urls:
        log.message("No links found to download")
        return item.derived_copy(
            format=Format.yaml, body=to_yaml_string(LinkResults(links=[]).model_dump())
        )

    download_result = asyncio.run(fetch_urls_async(urls))

    log.message(f"Downloaded {len(download_result.links)} links")
    if download_result.total_errors > 0:
        log.warning(
            "Failed to download %d out of %d links",
            download_result.total_errors,
            download_result.total_attempted,
        )

    # Print concise histogram: tallies by HTTP status code
    code_counts = download_result.histogram()
    if code_counts:
        lines = ["by_status_code:"]
        lines.extend(f"  {code}: {count}" for code, count in sorted(code_counts.items()))
        log.message("Status code tallies:\n%s", fmt_lines(lines))

    results = LinkResults(links=download_result.links)
    result_item = item.derived_copy(format=Format.yaml, body=to_yaml_string(results.model_dump()))
    return result_item


## Tests


def test_fetch_links_no_links():
    from kash.model import Format, ItemType

    item = Item(
        type=ItemType.doc,
        format=Format.markdown,
        body="This is just plain text with no links at all.",
    )
    result = fetch_links(item)
    assert result.format == Format.yaml
    assert result.body is not None
    assert "links: []" in result.body


def test_fetch_links_with_mock_links():
    """Test the link extraction part without actually downloading URLs."""
    from textwrap import dedent

    from kash.utils.text_handling.markdown_utils import extract_urls

    markdown_content = dedent("""
        # Test Document
        
        Check out [GitHub](https://github.com) for code repositories.
        
        You can also visit [Python.org](https://python.org) for documentation.
        """).strip()

    links = extract_urls(markdown_content, include_internal=False)
    assert len(links) == 2
    assert "https://github.com" in links
    assert "https://python.org" in links


def test_fetch_links_with_links_data():
    """Test fetch_links with a pre-existing links data item."""
    from kash.kits.docs.links.links_model import Link
    from kash.model import Format, ItemType

    links = [
        Link(url="https://example.com"),
        Link(url="https://test.com"),
    ]
    results = LinkResults(links=links)

    # Use utility function to create the test item
    item = Item(type=ItemType.data, format=Format.yaml, body="dummy")
    test_item = item.derived_copy(format=Format.yaml, body=to_yaml_string(results.model_dump()))

    # Verify precondition works
    assert is_links_data(test_item)

    # Note: This test won't actually download since we're testing with fake URLs
    # The real download would happen with valid URLs
