def test_table_render_basic():
    from items import Table

    t = Table(header="H", body="| a |\n| - |\n| 1 |", footer="f")
    out = t.render()
    assert out.startswith("### H")
    assert "| a |" in out
    assert out.rstrip().endswith("_f_")


def test_paragraph_render_basic():
    from items import Paragraph

    p = Paragraph(text="hello")
    assert p.render() == "hello"


def test_list_render_layout():
    from items import List

    lst = List(items=[1, 2, 3, 4])
    out = lst.render()
    # First row has 3 entries, last row has remainder (1 item)
    assert "1" in out and "2" in out and "3" in out and "4" in out
