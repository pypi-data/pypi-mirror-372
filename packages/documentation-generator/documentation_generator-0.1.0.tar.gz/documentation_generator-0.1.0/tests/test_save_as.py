from pathlib import Path
import pytest


def test_save_as_md_and_html(tmp_path, monkeypatch):
    from document import Document
    monkeypatch.chdir(tmp_path)

    doc = Document().add_paragraph("Hello", heading="Title").add_list(["a", "b", "c", "d"], heading="List")

    md_path = Path(doc.save_as("md"))
    assert md_path.name == "document.md" and md_path.exists()
    content = md_path.read_text(encoding="utf-8")
    assert "### Title" in content and "Hello" in content

    html_path = Path(doc.save_as("html"))
    assert html_path.name == "document.html" and html_path.exists()
    html = html_path.read_text(encoding="utf-8")
    assert "<!doctype html>" in html and "<h3>Title</h3>" in html


def test_save_as_pdf(tmp_path, monkeypatch):
    weasyprint = pytest.importorskip("weasyprint")
    from document import Document
    monkeypatch.chdir(tmp_path)

    doc = Document().add_paragraph("Hello PDF", heading="PDF")
    pdf_path = Path(doc.save_as("pdf"))
    assert pdf_path.name == "document.pdf" and pdf_path.exists() and pdf_path.stat().st_size > 0
