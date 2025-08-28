from dataclasses import dataclass, field
from typing import Any
from abc import ABC, abstractmethod

try:  # optional dependency
    from tabulate import tabulate  # type: ignore
except Exception:  # pragma: no cover
    tabulate = None  # type: ignore


class DocumentPart(ABC):
    @abstractmethod
    def render(self) -> str:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class Paragraph(DocumentPart):
    text: str = ""

    def render(self) -> str:
        return self.text


@dataclass
class Table(DocumentPart):
    header: str = ""
    body: str = ""
    footer: str = ""

    def render(self) -> str:
        parts: list[str] = []
        if self.header:
            parts.append(f"### {self.header}")
        if self.body:
            parts.append(self.body)
        if self.footer:
            parts.append(f"_{self.footer}_")
        return "\n".join(parts)


@dataclass
class List(DocumentPart):
    items: list[Any] = field(default_factory=list)
    ordered: bool = False

    def render(self) -> str:
        data = [str(x) for x in self.items]
        cols = 3
        n = len(data)

        rows: list[list[str]] = []
        full_rows = n // cols
        for i in range(full_rows):
            start = i * cols
            rows.append(data[start : start + cols])
        # last row with n % 3 elements (can be empty)
        start = full_rows * cols
        rows.append(data[start : start + (n % cols)])

        if tabulate is not None:
            return tabulate(rows, tablefmt="github")
        # Fallback: simple row-joined markdown without headers
        return "\n".join("| " + " | ".join(r) + " |" for r in rows)


@dataclass
class CodeBlock(DocumentPart):
    code: str
    language: str = ""

    def render(self) -> str:
        lang = self.language.strip()
        prefix = f"```{lang}" if lang else "```"
        return f"{prefix}\n{self.code}\n```"


@dataclass
class Remark(DocumentPart):
    kind: str  # e.g., INFO, WARNING, DANGER, TIP
    text: str

    def render(self) -> str:
        label = (self.kind or "info").strip().lower()
        # Indent each content line by 4 spaces for admonition body
        body = "\n".join("    " + line for line in self.text.splitlines() or [""])
        return f"!!! {label}\n{body}"

