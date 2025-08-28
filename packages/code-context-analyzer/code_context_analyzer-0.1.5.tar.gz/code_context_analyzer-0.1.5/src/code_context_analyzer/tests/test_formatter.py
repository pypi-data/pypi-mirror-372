from code_context_analyzer.analyzer.formatter import Formatter


def test_formatter_basic():
    parsed_data = [
        {"path": "file1.py", "functions": ["foo", "bar"], "classes": ["A"]},
        {"path": "file2.py", "functions": ["baz"], "classes": []}
    ]
    formatter = Formatter(depth=2, method_preview=10, doc_chars=220)
    result = formatter.format_project(parsed_data)
    assert "2 file(s)" in result
    assert "1 class(es)" in result
    assert "3 function(s)" in result
    assert "foo" in result
