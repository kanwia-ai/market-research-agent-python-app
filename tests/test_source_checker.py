"""Tests for HTTP-based source URL verification."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.source_checker import (
    SourceCheckResult,
    check_url,
    extract_urls,
    verify_report_sources,
)


class TestExtractUrls:
    """Tests for the extract_urls function."""

    def test_finds_urls_in_text(self):
        """Extract URLs finds HTTP and HTTPS URLs in text."""
        text = "Check out https://example.com and http://test.org for details."
        urls = extract_urls(text)
        assert "https://example.com" in urls
        assert "http://test.org" in urls

    def test_deduplicates_urls(self):
        """Extract URLs removes duplicates while preserving order."""
        text = "Visit https://example.com then https://other.com then https://example.com again."
        urls = extract_urls(text)
        assert urls == ["https://example.com", "https://other.com"]

    def test_strips_trailing_punctuation(self):
        """Extract URLs strips trailing punctuation that is not part of the URL."""
        text = "See https://example.com. Also https://test.org, and https://foo.bar!"
        urls = extract_urls(text)
        assert "https://example.com" in urls
        assert "https://test.org" in urls
        assert "https://foo.bar" in urls
        # Ensure punctuation was stripped
        for url in urls:
            assert not url.endswith(".")
            assert not url.endswith(",")
            assert not url.endswith("!")

    def test_returns_empty_list_for_no_urls(self):
        """Extract URLs returns empty list when no URLs are present."""
        text = "This text has no URLs at all."
        urls = extract_urls(text)
        assert urls == []

    def test_returns_empty_list_for_empty_string(self):
        """Extract URLs returns empty list for empty input."""
        assert extract_urls("") == []

    def test_finds_urls_in_markdown(self):
        """Extract URLs finds URLs in markdown link syntax."""
        text = "Read [this article](https://example.com/article) for more info."
        urls = extract_urls(text)
        assert "https://example.com/article" in urls


class TestSourceCheckResult:
    """Tests for the SourceCheckResult dataclass."""

    def test_creation_with_required_fields(self):
        """SourceCheckResult can be created with just url and status."""
        result = SourceCheckResult(url="https://example.com", status="alive")
        assert result.url == "https://example.com"
        assert result.status == "alive"
        assert result.status_code is None
        assert result.redirect_url is None
        assert result.error is None

    def test_creation_with_all_fields(self):
        """SourceCheckResult can be created with all fields."""
        result = SourceCheckResult(
            url="https://example.com",
            status="alive",
            status_code=200,
            redirect_url="https://www.example.com",
            error=None,
        )
        assert result.status_code == 200
        assert result.redirect_url == "https://www.example.com"

    def test_creation_with_error(self):
        """SourceCheckResult stores error information."""
        result = SourceCheckResult(
            url="https://bad.example",
            status="error",
            error="Connection refused",
        )
        assert result.status == "error"
        assert result.error == "Connection refused"


class TestCheckUrl:
    """Tests for the check_url function."""

    @pytest.mark.asyncio
    async def test_returns_alive_for_200(self):
        """check_url returns alive status for HTTP 200 response."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.url = "https://example.com"
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.head = MagicMock(return_value=mock_response)

        result = await check_url(mock_session, "https://example.com")
        assert result.status == "alive"
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_dead_for_404(self):
        """check_url returns dead status for HTTP 404 response."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.url = "https://example.com/missing"
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.head = MagicMock(return_value=mock_response)

        result = await check_url(mock_session, "https://example.com/missing")
        assert result.status == "dead"
        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_invalid_for_malformed_url(self):
        """check_url returns invalid status for a malformed URL."""
        mock_session = AsyncMock()
        result = await check_url(mock_session, "not-a-url")
        assert result.status == "invalid"
        assert result.error == "Malformed URL"

    @pytest.mark.asyncio
    async def test_returns_timeout_on_timeout(self):
        """check_url returns timeout status when request times out."""
        mock_session = AsyncMock()
        mock_session.head = MagicMock(side_effect=asyncio.TimeoutError())

        result = await check_url(mock_session, "https://slow.example.com")
        assert result.status == "timeout"
        assert result.error == "Request timed out"


class TestVerifyReportSources:
    """Tests for the verify_report_sources function."""

    @pytest.mark.asyncio
    async def test_returns_empty_summary_for_no_urls(self):
        """verify_report_sources returns zeroed summary when no URLs found."""
        result = await verify_report_sources("No links here.")
        assert result["total_urls"] == 0
        assert result["alive"] == 0
        assert result["dead"] == 0
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_aggregates_results_correctly(self):
        """verify_report_sources correctly aggregates check results."""
        report = "See https://good.com and https://bad.com for details."

        mock_results = [
            SourceCheckResult(url="https://good.com", status="alive", status_code=200),
            SourceCheckResult(url="https://bad.com", status="dead", status_code=404),
        ]

        with patch("src.source_checker.check_urls", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_results
            result = await verify_report_sources(report)

        assert result["total_urls"] == 2
        assert result["alive"] == 1
        assert result["dead"] == 1
        assert len(result["dead_urls"]) == 1
        assert result["dead_urls"][0]["url"] == "https://bad.com"
        assert len(result["results"]) == 2
