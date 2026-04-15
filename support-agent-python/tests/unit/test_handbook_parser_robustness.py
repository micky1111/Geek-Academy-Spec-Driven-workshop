from app.processor import parse_handbook_sections


def test_handbook_parser_extracts_multiple_sections():
    handbook = """\
## Section A
Content A
## Section B
Content B
"""
    sections = parse_handbook_sections(handbook)
    assert len(sections) == 2
    assert sections[0]["title"] == "Section A"
    assert "Content B" in sections[1]["content"]


def test_handbook_parser_handles_empty_input():
    sections = parse_handbook_sections("")
    assert sections == []
