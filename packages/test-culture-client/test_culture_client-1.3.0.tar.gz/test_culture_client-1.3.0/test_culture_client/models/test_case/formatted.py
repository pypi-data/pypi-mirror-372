import json

# Table -> N*TableRow -> M*TableCell or M*TableHeader -> F*TableCells -> Content

_LINE_BREAK = {"type": "hardBreak"}


def wrap_line(line: str) -> list[dict]:
    return {"type": "text", "text": line}


def wrap_paragraph(paragraph: str) -> dict:
    content = []
    for line in paragraph.splitlines():
        content.append(wrap_line(line))
        content.append(_LINE_BREAK)
    return {
        "type": "paragraph",
        "attrs": {"indent": 0, "textAlign": "justify"},
        "content": content[:-1],
    }


def wrap_simple_table_cell(content: str) -> dict:
    return wrap_table_cell([wrap_paragraph(content)])


def wrap_table_cell(content: list[dict]) -> dict:
    return {
        "type": "tableCell",
        "attrs": {
            "colspan": 1,
            "rowspan": 1,
            "colwidth": None,
            "backgroundColor": None,
        },
        "content": content,
    }


def wrap_table_row(cells: list[dict]) -> dict:
    return {"type": "tableRow", "content": cells}


def wrap_table_header(content: list[dict]) -> dict:
    return {
        "type": "tableHeader",
        "attrs": {
            "colspan": 1,
            "rowspan": 1,
            "colwidth": None,
            "backgroundColor": "var(--editor-highlight-bgc)",
        },
        "content": content,
    }


def wrap_table(rows: list[dict], column_widths: list[int]) -> dict:
    return {
        "type": "table",
        "attrs": {
            "columnWidths": column_widths,
            "filters": [],
            "sort": None,
            "summaryRow": {},
            "calcColumn": None,
            "style": None,
        },
        "content": rows,
    }


def build_formatted_text(contents: list[dict]) -> str:
    return json.dumps({"type": "doc", "content": contents})
