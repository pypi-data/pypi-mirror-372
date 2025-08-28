from __future__ import annotations

from typing import Iterable
from pathlib import Path
import shutil

try:  # optional
    from weasyprint import HTML  # type: ignore
except Exception:  # pragma: no cover
    HTML = None  # type: ignore

from .items import DocumentPart


def render_markdown(parts: Iterable[DocumentPart]) -> str:
    return "\n".join(p.render() for p in parts)


def markdown_to_html(md_text: str) -> str:
    try:
        import markdown as _markdown  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Markdown library not installed. Please `pip install Markdown`.") from e

    try:
        html_body = _markdown.markdown(
            md_text,
            extensions=["tables", "admonition", "fenced_code"],  # type: ignore[arg-type]
        )
    except Exception:
        html_body = _markdown.markdown(md_text)
    html_doc = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<link rel=\"stylesheet\" href=\"assets/shadcdn.css\">"
        "</head><body>" + html_body + "</body></html>"
    )
    return html_doc


def write_pdf_from_html(html_doc: str, out_path: str) -> None:
    if HTML is None:
        raise RuntimeError("WeasyPrint not installed. Please `pip install weasyprint` to save as PDF.")
    # Set base_url so linked assets like CSS resolve from CWD or provided path
    HTML(string=html_doc, base_url=str(Path.cwd())).write_pdf(out_path)


def ensure_assets(out_dir: str | Path) -> None:
    """Copy static assets (CSS, etc.) next to generated documents.

    Copies the local assets folder to the destination directory so that
    links like `assets/shadcdn.css` resolve when opening the HTML or when
    rendering to PDF.
    """
    try:
        src_assets = Path(__file__).with_name("assets")
        if not src_assets.exists():
            return
        dest_assets = Path(out_dir) / "assets"
        dest_assets.mkdir(parents=True, exist_ok=True)
        for name in ("shadcdn.css",):
            src_file = src_assets / name
            if src_file.exists():
                shutil.copy2(src_file, dest_assets / name)
    except Exception:
        # Best-effort: don't block document generation on asset copy
        pass

