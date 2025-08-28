import pytest


def test_paragraph_and_list_render_chaining():
    from document import Document

    doc = Document()
    doc = doc.add_paragraph("Hello world", heading="Intro").add_list(
        [1, 2, 3, 4], heading="Nums"
    )
    out = doc.render()

    assert "### Intro" in out
    assert "Hello world" in out
    assert "### Nums" in out
    # Expect two rows: first with 1|2|3, second with 4 only
    assert "| 1 | 2 | 3 |" in out or "1 | 2 | 3" in out
    assert "| 4 |" in out or "| 4" in out


def test_table_render_with_pandas():
    pandas = pytest.importorskip("pandas")
    from document import Document

    df = pandas.DataFrame({"a": [1, 2], "b": [3, 4]})

    doc = Document().add_table(df, heading="MyTable", footer="note")
    out = doc.render()

    # Table.render renders header with ### and footer in italics
    assert "### MyTable" in out
    assert "_note_" in out
    # Expect a markdown table pipe characters
    assert "| a" in out and "| b" in out
