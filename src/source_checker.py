"""HTTP-based source URL verification."""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

import aiohttp

logger = logging.getLogger(__name__)

# Timeout per request
REQUEST_TIMEOUT = 10  # seconds
# Max concurrent requests
MAX_CONCURRENT = 10


@dataclass
class SourceCheckResult:
    """Result of checking a single URL."""
    url: str
    status: str  # "alive", "dead", "timeout", "invalid", "error"
    status_code: int | None = None
    redirect_url: str | None = None
    error: str | None = None


# Regex to extract URLs from markdown text
_URL_RE = re.compile(r'https?://[^\s)\]>"\']+')


def extract_urls(text: str) -> list[str]:
    """Extract all HTTP/HTTPS URLs from text."""
    urls = _URL_RE.findall(text)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for url in urls:
        # Strip trailing punctuation that isn't part of URL
        url = url.rstrip(".,;:!?")
        if url not in seen:
            seen.add(url)
            unique.append(url)
    return unique


async def check_url(session: aiohttp.ClientSession, url: str) -> SourceCheckResult:
    """Check a single URL with HTTP HEAD (falling back to GET)."""
    # Validate URL format first
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return SourceCheckResult(url=url, status="invalid", error="Malformed URL")

    try:
        async with session.head(
            url,
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
            allow_redirects=True,
            ssl=False,
        ) as resp:
            redirect_url = str(resp.url) if str(resp.url) != url else None
            if resp.status < 400:
                return SourceCheckResult(
                    url=url, status="alive",
                    status_code=resp.status,
                    redirect_url=redirect_url,
                )
            elif resp.status == 405:
                # HEAD not allowed, try GET
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                    allow_redirects=True,
                    ssl=False,
                ) as get_resp:
                    redirect_url = str(get_resp.url) if str(get_resp.url) != url else None
                    status = "alive" if get_resp.status < 400 else "dead"
                    return SourceCheckResult(
                        url=url, status=status,
                        status_code=get_resp.status,
                        redirect_url=redirect_url,
                    )
            else:
                return SourceCheckResult(
                    url=url, status="dead",
                    status_code=resp.status,
                )
    except asyncio.TimeoutError:
        return SourceCheckResult(url=url, status="timeout", error="Request timed out")
    except aiohttp.ClientError as e:
        return SourceCheckResult(url=url, status="error", error=str(e))
    except Exception as e:
        return SourceCheckResult(url=url, status="error", error=str(e))


async def check_urls(urls: list[str]) -> list[SourceCheckResult]:
    """Check multiple URLs concurrently with a semaphore."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def limited_check(session, url):
        async with semaphore:
            return await check_url(session, url)

    headers = {"User-Agent": "MarketResearchBot/1.0 (source verification)"}
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [limited_check(session, url) for url in urls]
        return await asyncio.gather(*tasks)


async def verify_report_sources(report_text: str) -> dict:
    """Extract URLs from a report and verify them all.

    Returns a summary dict with:
    - total_urls: int
    - alive: int
    - dead: int
    - timeout: int
    - errors: int
    - dead_urls: list of dead URL details
    - results: list of all SourceCheckResult as dicts
    """
    urls = extract_urls(report_text)
    if not urls:
        return {"total_urls": 0, "alive": 0, "dead": 0, "timeout": 0, "errors": 0, "dead_urls": [], "results": []}

    logger.info("Checking %d URLs from report", len(urls))
    results = await check_urls(urls)

    alive = sum(1 for r in results if r.status == "alive")
    dead = sum(1 for r in results if r.status == "dead")
    timeout = sum(1 for r in results if r.status == "timeout")
    errors = sum(1 for r in results if r.status in ("error", "invalid"))

    dead_urls = [
        {"url": r.url, "status_code": r.status_code, "error": r.error}
        for r in results if r.status in ("dead", "error", "invalid")
    ]

    logger.info(
        "Source check complete: %d alive, %d dead, %d timeout, %d errors out of %d total",
        alive, dead, timeout, errors, len(urls),
    )

    return {
        "total_urls": len(urls),
        "alive": alive,
        "dead": dead,
        "timeout": timeout,
        "errors": errors,
        "dead_urls": dead_urls,
        "results": [
            {"url": r.url, "status": r.status, "status_code": r.status_code,
             "redirect_url": r.redirect_url, "error": r.error}
            for r in results
        ],
    }
