# documentation-generator

Tiny, composable Markdown document builder with optional HTML/PDF export.

Features
- Build documents by chaining: paragraphs, tables, lists, code blocks, and remarks.
- Render to Markdown; convert to HTML (Markdown lib) or PDF (WeasyPrint).
- Tables render in GitHub‑style Markdown (via tabulate).

Requirements
- Python 3.13+

Installation
```bash
pip install -e .           # install project (editable)
# or just runtime deps
pip install tabulate Markdown
# to enable PDF export
pip install weasyprint
# dev/test extras
pip install -e .[dev]
```

Quick Start
```python
from document import Document
import pandas as pd

doc = (
    Document()
      .add_title("Sample Doc")
      .add_paragraph("Intro text", heading="Introduction")
      .add_list(["alpha", "beta", "gamma", "delta"], heading="Things")
      .add_codeblock("print('hello')", language="python")
      .add_remark("Remember to pin versions.", kind="TIP")
)

# Tables accept pandas or polars DataFrame
df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
doc.add_table(df, heading="Data", footer="auto‑generated")

# Render as Markdown string
markdown_text = doc.render()
print(markdown_text)

# Save to files
doc.save_as("md")    # writes document.md
doc.save_as("html")  # writes document.html
# Requires: pip install weasyprint
doc.save_as("pdf")   # writes document.pdf
```

Remarks (Admonitions)
- `add_remark(text, kind)` supports: `INFO`, `WARNING`, `DANGER`, `TIP`.
- Uses Markdown admonition syntax, e.g. `!!! warning`.
- HTML conversion enables `admonition`, `tables`, and `fenced_code` extensions.

Testing
```bash
pip install -e .[dev]
pytest -q
```
