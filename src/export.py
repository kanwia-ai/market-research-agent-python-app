"""Export utilities for research reports."""

import io
import json
import zipfile
from datetime import datetime
from typing import Optional

import markdown2
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt


def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML with styling."""
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            "fenced-code-blocks",
            "tables",
            "header-ids",
            "strike",
            "task_list",
        ],
    )

    # Wrap in styled HTML document
    styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #1a1a2e;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        h1 {{
            color: #007A75;
            border-bottom: 3px solid #007A75;
            padding-bottom: 10px;
            font-size: 28px;
        }}

        h2 {{
            color: #1a1a2e;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 22px;
        }}

        h3 {{
            color: #333;
            margin-top: 25px;
            font-size: 18px;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        th {{
            background-color: #007A75;
            color: white;
        }}

        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        blockquote {{
            border-left: 4px solid #007A75;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8fafa;
            font-style: italic;
        }}

        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Fira Code', monospace;
        }}

        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}

        a {{
            color: #007A75;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 8px 0;
        }}

        .source-citation {{
            font-size: 0.9em;
            color: #666;
        }}

        @media print {{
            body {{
                max-width: none;
                padding: 20px;
            }}

            h1, h2, h3 {{
                page-break-after: avoid;
            }}

            table, blockquote {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
    return styled_html


def export_to_pdf(markdown_content: str, title: str = "Research Report") -> bytes:
    """Export markdown content to PDF bytes."""
    try:
        from weasyprint import HTML

        html_content = markdown_to_html(markdown_content)
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except ImportError:
        raise ImportError(
            "weasyprint is required for PDF export. "
            "Install it with: pip install weasyprint"
        )
    except Exception as e:
        raise RuntimeError(f"PDF generation failed: {e}")


def export_to_docx(markdown_content: str, title: str = "Research Report") -> bytes:
    """Export markdown content to DOCX bytes."""
    doc = Document()

    # Add title
    title_para = doc.add_heading(title, 0)
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Add generation date
    date_para = doc.add_paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()  # Spacer

    # Parse markdown and add content
    lines = markdown_content.split("\n")
    in_code_block = False
    code_content = []

    for line in lines:
        # Handle code blocks
        if line.startswith("```"):
            if in_code_block:
                # End code block
                code_text = "\n".join(code_content)
                code_para = doc.add_paragraph(code_text)
                code_para.style = "No Spacing"
                for run in code_para.runs:
                    run.font.name = "Courier New"
                    run.font.size = Pt(9)
                code_content = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_content.append(line)
            continue

        # Handle headings
        if line.startswith("# "):
            doc.add_heading(line[2:], 1)
        elif line.startswith("## "):
            doc.add_heading(line[3:], 2)
        elif line.startswith("### "):
            doc.add_heading(line[4:], 3)
        elif line.startswith("#### "):
            doc.add_heading(line[5:], 4)
        # Handle blockquotes
        elif line.startswith("> "):
            quote_para = doc.add_paragraph(line[2:])
            quote_para.style = "Quote"
        # Handle bullet points
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:], style="List Bullet")
        # Handle numbered lists
        elif line and line[0].isdigit() and ". " in line[:4]:
            text = line.split(". ", 1)[1] if ". " in line else line
            doc.add_paragraph(text, style="List Number")
        # Handle horizontal rules
        elif line.startswith("---"):
            doc.add_paragraph("─" * 50)
        # Handle regular paragraphs
        elif line.strip():
            doc.add_paragraph(line)

    # Save to bytes
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def create_asset_bundle(
    report_markdown: str,
    raw_findings: Optional[dict] = None,
    title: str = "research_report",
) -> bytes:
    """Create a ZIP bundle with all research assets."""
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add the main report as markdown
        zf.writestr(f"{title}.md", report_markdown)

        # Add HTML version
        html_content = markdown_to_html(report_markdown)
        zf.writestr(f"{title}.html", html_content)

        # Try to add PDF version
        try:
            pdf_bytes = export_to_pdf(report_markdown, title)
            zf.writestr(f"{title}.pdf", pdf_bytes)
        except Exception:
            pass  # Skip PDF if generation fails

        # Add DOCX version
        try:
            docx_bytes = export_to_docx(report_markdown, title)
            zf.writestr(f"{title}.docx", docx_bytes)
        except Exception:
            pass  # Skip DOCX if generation fails

        # Add raw findings if provided
        if raw_findings:
            # Create raw_data directory in zip
            for agent_name, findings in raw_findings.items():
                if isinstance(findings, dict):
                    content = json.dumps(findings, indent=2, default=str)
                    zf.writestr(f"raw_data/{agent_name}.json", content)
                else:
                    zf.writestr(f"raw_data/{agent_name}.txt", str(findings))

        # Add metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "title": title,
            "files_included": [
                f"{title}.md",
                f"{title}.html",
                f"{title}.pdf",
                f"{title}.docx",
            ],
        }
        if raw_findings:
            metadata["raw_data_files"] = list(raw_findings.keys())

        zf.writestr("metadata.json", json.dumps(metadata, indent=2))

    buffer.seek(0)
    return buffer.getvalue()


def get_filename_from_title(title: str, extension: str = "") -> str:
    """Generate a safe filename from a title."""
    # Remove special characters and replace spaces
    safe_title = "".join(
        c if c.isalnum() or c in " -_" else "" for c in title
    ).strip()
    safe_title = safe_title.replace(" ", "-").lower()

    # Add date prefix
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-{safe_title}"

    if extension:
        filename = f"{filename}.{extension.lstrip('.')}"

    return filename
