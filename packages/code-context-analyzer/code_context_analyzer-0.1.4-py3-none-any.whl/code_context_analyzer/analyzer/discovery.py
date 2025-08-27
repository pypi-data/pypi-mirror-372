"""Discover files to analyze."""
import os
from typing import List, Tuple

EXT_MAP = {"py": [".py"], "js": [".js"], "ts": [".ts", ".tsx"]}


def discover_files(
    root: str,
    languages: list[str],
    max_files: int = 1000,
    ignore_tests: bool = True
) -> List[Tuple[str, str]]:
    """
        Walks root and yields (path, language) tuples.
        Simple, but respects .gitignore (basic) by skipping hidden directories
        and __pycache__.
    """
    out = []
    exts = {lang: EXT_MAP.get(lang, []) for lang in languages}
    for dirpath, dirnames, filenames in os.walk(root):
        rel = os.path.relpath(dirpath, root)

        # skip hidden dirs (but allow root itself)
        if rel != "." and any(p.startswith('.') for p in rel.split(os.sep)):
            continue

        if 'node_modules' in dirpath or '__pycache__' in dirpath:
            continue

        for name in filenames:
            if ignore_tests and name.lower().startswith('test'):
                continue
            if name.startswith('.') or name.startswith('._'):
                continue
            for lang, extlist in exts.items():
                if any(name.endswith(ext) for ext in extlist):
                    out.append((os.path.join(dirpath, name), lang))
                    break
            if len(out) >= max_files:
                return out
    return out
