def test_codeblock_and_remark_render():
    from document import Document

    doc = (
        Document()
        .add_paragraph("Intro")
        .add_codeblock("print('hi')", language="python")
        .add_remark("Be careful!", kind="WARNING")
    )
    md = doc.render()

    assert "```python" in md and "print('hi')" in md and md.count("```") >= 2
    assert "!!! warning" in md and "Be careful!" in md
