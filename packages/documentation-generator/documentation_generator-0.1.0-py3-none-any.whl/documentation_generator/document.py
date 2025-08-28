from dataclasses import dataclass, field
from typing import Any
from .items import Paragraph, Table, List as ListItem, DocumentPart, CodeBlock, Remark
from .render import render_markdown, markdown_to_html, write_pdf_from_html, ensure_assets

# Optional imports for DataFrame support
try:  # pragma: no cover - optional dependency
    import polars as pl  # type: ignore
except Exception:  # pragma: no cover
    pl = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from tabulate import tabulate  # type: ignore
except Exception:  # pragma: no cover
    tabulate = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import markdown as md_lib  # type: ignore
except Exception:  # pragma: no cover
    md_lib = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from weasyprint import HTML  # type: ignore
except Exception:  # pragma: no cover
    HTML = None  # type: ignore


@dataclass
class Document:
    items: list[DocumentPart] = field(default_factory=list)

    def add_title(self, text: str) -> "Document":
        if text:
            self.items.append(Paragraph(text=f"# {text}"))
        return self

    def add_section(self, text: str) -> "Document":
        if text:
            self.items.append(Paragraph(text=f"## {text}"))
        return self

    def add_paragraph(self, text: str, heading: str = "") -> "Document":
        if heading:
            self.items.append(Paragraph(text=f"### {heading}"))
        self.items.append(Paragraph(text=text))
        return self

    def add_table(self, data: Any, heading: str = "", footer: str = "") -> "Document":
        # Normalize input to a pandas DataFrame for compatibility
        df = None
        if pl is not None and isinstance(data, pl.DataFrame):  # type: ignore[attr-defined]
            try:
                df = data.to_pandas()
            except Exception:
                pass
        if df is None and pd is not None and isinstance(data, pd.DataFrame):  # type: ignore[attr-defined]
            df = data
        if df is None:
            raise TypeError("data must be a polars.DataFrame or pandas.DataFrame")

        # Produce markdown table text using tabulate if available
        md_text = ""
        if tabulate is not None:
            try:
                md_text = tabulate(
                    df, headers="keys", tablefmt="github", showindex=False
                )
            except Exception:
                md_text = ""

        if not md_text:
            # Fallback: build a simple GitHub-flavored Markdown table
            try:
                df_str = df.fillna("").astype(str)
            except Exception:
                df_str = df.astype(str)
            headers = [str(h) for h in getattr(df_str, "columns", [])]
            if headers:
                header_line = "| " + " | ".join(headers) + " |"
                sep_line = "| " + " | ".join(["---"] * len(headers)) + " |"
                rows = df_str.values.tolist()
                row_lines = ["| " + " | ".join(map(str, r)) + " |" for r in rows]
                md_text = "\n".join([header_line, sep_line, *row_lines])
            else:
                md_text = ""
        table = Table(header=heading or "", body=md_text, footer=footer)
        self.items.append(table)
        return self

    def add_list(self, items: list[Any], heading: str = "") -> "Document":
        if heading:
            self.items.append(Paragraph(text=f"### {heading}"))
        lst = ListItem(items=list(items))
        self.items.append(lst)
        return self

    def add_codeblock(self, code: str, language: str = "") -> "Document":
        self.items.append(CodeBlock(code=code, language=language))
        return self

    def add_remark(self, text: str, kind: str = "INFO") -> "Document":
        self.items.append(Remark(kind=kind, text=text))
        return self

    def render(self) -> str:
        return render_markdown(self.items)

    def save_as(self, extension: str, filename:str) -> str:
        ext = extension.lower().lstrip(".")
        if ext not in {"md", "html", "pdf"}:
            raise ValueError("extension must be one of: 'md', 'html', 'pdf'")

        md_text = self.render()

        if ext == "md":
            out_path = f"{filename}.md"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md_text)
            return out_path

        html_doc = markdown_to_html(md_text)

        if ext == "html":
            out_path = f"{filename}.html"
            ensure_assets(".")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_doc)
            return out_path

        out_path = f"{filename}.pdf"
        ensure_assets(".")
        write_pdf_from_html(html_doc, out_path)
        return out_path

