"""CLI entrypoint for cca."""
import argparse
import sys

from code_context_analyzer.analyzer import run_analysis
from code_context_analyzer.analyzer.repository_handler import RepositoryHandler


def app(argv=None):
    parser = argparse.ArgumentParser(prog="cca", description="Codebase Context Analyzer")
    parser.add_argument("source", help="Local path or GitHub repository URL")
    parser.add_argument("--branch", default="main", help="Branch name (for GitHub repos)")
    parser.add_argument("--languages", default="py", help="Comma-separated languages to analyze (py,js,ts)")
    parser.add_argument("--max-files", type=int, default=1000, help="Max files to analyze")
    parser.add_argument("--depth", type=int, default=3, help="Module depth to summarize")
    parser.add_argument("--ignore-tests", type=str, default=True, help="Ignore all the tests start with tests")
    parser.add_argument("--no-clipboard", action="store_true", help="Do not copy to clipboard")
    args = parser.parse_args(argv)

    repository_handler = RepositoryHandler()
    local_path = repository_handler.resolve_source(args.source, args.branch)
    result = run_analysis(path=local_path, languages=args.languages.split(","), max_files=args.max_files, depth=args.depth, ignore_tests=args.ignore_tests)

    print(result)

    if not args.no_clipboard:
        try:
            from code_context_analyzer.analyzer.clipboard import copy_to_clipboard
            copy_to_clipboard(result)
            print("[info] Copied summary to clipboard")
        except Exception as e:
            print(f"[warn] Clipboard copy failed: {e}")


if __name__ == '__main__':
    app(sys.argv[1:])
