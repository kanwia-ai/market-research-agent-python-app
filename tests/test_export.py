"""Tests for export functionality."""

import json
import zipfile
from io import BytesIO

from src.export import (
    create_asset_bundle,
    export_to_docx,
    get_filename_from_title,
    markdown_to_html,
)


class TestMarkdownToHtml:
    """Tests for markdown to HTML conversion."""

    def test_converts_basic_markdown(self):
        """Test basic markdown conversion."""
        md = "# Hello World\n\nThis is a paragraph."
        html = markdown_to_html(md)
        assert "<h1" in html
        assert "Hello World" in html
        assert "<p>" in html

    def test_includes_styling(self):
        """Test that HTML includes CSS styling."""
        md = "# Test"
        html = markdown_to_html(md)
        assert "<style>" in html
        assert "font-family" in html

    def test_handles_tables(self):
        """Test table conversion."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = markdown_to_html(md)
        assert "<table>" in html

    def test_handles_code_blocks(self):
        """Test code block conversion."""
        md = "```python\nprint('hello')\n```"
        html = markdown_to_html(md)
        assert "<code" in html or "<pre" in html


class TestExportToDocx:
    """Tests for DOCX export."""

    def test_returns_bytes(self):
        """Test that export returns bytes."""
        md = "# Test Report\n\nSome content."
        result = export_to_docx(md, "Test")
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_creates_valid_docx(self):
        """Test that output is valid DOCX (ZIP format)."""
        md = "# Test\n\n- Item 1\n- Item 2"
        result = export_to_docx(md)
        # DOCX files are ZIP archives
        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            # DOCX must contain these files
            assert "word/document.xml" in zf.namelist()

    def test_handles_headings(self):
        """Test heading conversion."""
        md = "# H1\n## H2\n### H3"
        result = export_to_docx(md)
        assert len(result) > 0

    def test_handles_lists(self):
        """Test list conversion."""
        md = "- Bullet 1\n- Bullet 2\n\n1. Numbered 1\n2. Numbered 2"
        result = export_to_docx(md)
        assert len(result) > 0

    def test_handles_blockquotes(self):
        """Test blockquote conversion."""
        md = '> This is a quote\n> — Author'
        result = export_to_docx(md)
        assert len(result) > 0


class TestCreateAssetBundle:
    """Tests for asset bundle creation."""

    def test_returns_zip_bytes(self):
        """Test that bundle returns ZIP bytes."""
        md = "# Report"
        result = create_asset_bundle(md)
        assert isinstance(result, bytes)

        # Verify it's a valid ZIP
        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            assert len(zf.namelist()) > 0

    def test_includes_markdown_file(self):
        """Test that bundle includes markdown."""
        md = "# My Report"
        result = create_asset_bundle(md, title="test")

        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            assert "test.md" in zf.namelist()
            content = zf.read("test.md").decode("utf-8")
            assert "My Report" in content

    def test_includes_html_file(self):
        """Test that bundle includes HTML."""
        md = "# Report"
        result = create_asset_bundle(md, title="test")

        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            assert "test.html" in zf.namelist()

    def test_includes_docx_file(self):
        """Test that bundle includes DOCX."""
        md = "# Report"
        result = create_asset_bundle(md, title="test")

        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            assert "test.docx" in zf.namelist()

    def test_includes_metadata(self):
        """Test that bundle includes metadata."""
        md = "# Report"
        result = create_asset_bundle(md, title="test")

        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            assert "metadata.json" in zf.namelist()
            metadata = json.loads(zf.read("metadata.json"))
            assert "generated_at" in metadata
            assert metadata["title"] == "test"

    def test_includes_raw_findings(self):
        """Test that raw findings are included."""
        md = "# Report"
        findings = {
            "CommunityMapper": {"communities": ["reddit", "twitter"]},
            "VoiceMiner": {"quotes": ["quote1", "quote2"]},
        }
        result = create_asset_bundle(md, raw_findings=findings, title="test")

        buffer = BytesIO(result)
        with zipfile.ZipFile(buffer, "r") as zf:
            names = zf.namelist()
            assert "raw_data/CommunityMapper.json" in names
            assert "raw_data/VoiceMiner.json" in names


class TestGetFilenameFromTitle:
    """Tests for filename generation."""

    def test_generates_safe_filename(self):
        """Test safe filename generation."""
        result = get_filename_from_title("My Report", "pdf")
        assert ".pdf" in result
        assert "/" not in result
        assert "\\" not in result

    def test_includes_date_prefix(self):
        """Test that date is included."""
        result = get_filename_from_title("Test")
        # Should have YYYY-MM-DD format at start
        assert result[4] == "-"
        assert result[7] == "-"

    def test_handles_special_characters(self):
        """Test handling of special characters."""
        result = get_filename_from_title("Test: Report! @#$%", "md")
        assert ":" not in result
        assert "!" not in result
        assert "@" not in result

    def test_lowercase_output(self):
        """Test that output is lowercase."""
        result = get_filename_from_title("UPPERCASE Test")
        # After the date prefix
        assert "uppercase" in result or "test" in result
