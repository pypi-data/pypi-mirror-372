"""Top-level orchestration."""
from .discovery import discover_files
from .formatter import Formatter
from .parsers import registry


def run_analysis(
    path: str,
    languages: list[str],
    max_files: int = 1000,
    depth: int = 3,
    ignore_tests: bool = True
) -> str:
    files = discover_files(path, languages, max_files, ignore_tests)

    parsed = []
    for fpath, lang in files:
        parser = registry.get(lang)
        if not parser:
            continue
        try:
            parsed.append(parser.parse_file(fpath))
        except Exception as e:
            # tolerate failures; log in v2
            parsed.append({"path": fpath, "error": str(e)})

    formatter = Formatter(depth=depth)
    return formatter.format_project(parsed)
