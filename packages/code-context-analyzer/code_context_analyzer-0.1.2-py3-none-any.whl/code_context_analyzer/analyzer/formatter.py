import os
from typing import Any, Dict, List, Optional, Tuple


class Formatter:
    """
    Formatter produces a textual summary from parsed module data with improved
    hierarchy for large projects.

    :param depth: how many top-level classes/functions to list per module
    :param method_preview: how many methods to show per class
    :param doc_chars: maximum characters to include from docstrings
    (0 to disable docs)
    :param truncate_total: if set, when project summary is longer than this
    many characters, it will be truncated (useful for chat limits)
    """

    def __init__(
            self,
            depth: int = 3,
            method_preview: int = 5,
            doc_chars: int = 140,
            truncate_total: Optional[int] = None,
    ):
        self.depth = max(0, int(depth))
        self.method_preview = max(0, int(method_preview))
        self.doc_chars = int(doc_chars) if doc_chars is not None else 0
        self.truncate_total = int(truncate_total) if (truncate_total is not
                                                      None) else None

    def format_project(self, parsed: List[Dict[str, Any]]) -> str:
        """
        Main entry. Accepts the raw parser output (list of module dicts)
        and returns a multi-line string summary with package hierarchy.
        """
        if not parsed:
            return "No files were parsed."

        # Defensive: normalize parsed items to dicts
        modules = [
            m if isinstance(m, dict) else {"path": str(m)} for m in parsed
        ]

        # compute a reasonable 'root' so we can show relative paths
        root = self._compute_common_root([m.get("path", "") for m in modules])
        root_name = os.path.basename(root) if root else "Project"

        totals = self._compute_totals(modules)
        header = self._build_header(root_name, totals, len(modules))

        # Group modules by package (directory path)
        grouped = self._group_by_package(modules, root)

        lines: List[str] = [header, ""]

        # 1. Project Tree Overview (concise)
        lines.append("## Project Tree Overview")
        lines.extend(self._format_tree_overview(grouped))
        lines.append("")

        # 2. Detailed Structure
        lines.append("## Detailed Structure")
        lines.extend(self._format_detailed_structure(grouped))

        result = "\n".join(lines).strip()

        # Optional truncation for paste-limited contexts
        if self.truncate_total and len(result) > self.truncate_total:
            result = result[: self.truncate_total - 3] + "..."

        return result

    def _compute_common_root(self, paths: List[str]) -> Optional[str]:
        """Return the common prefix path or None if it cannot be determined."""
        non_empty = [p for p in paths if p]
        if not non_empty:
            return None
        try:
            root = os.path.commonpath(non_empty)
            return root
        except Exception:
            return None

    def _compute_totals(self, modules: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count classes, functions and constants across modules."""
        total_classes = 0
        total_functions = 0
        total_constants = 0
        for mod in modules:
            if mod.get("error"):
                continue
            total_classes += len(mod.get("classes", []) or [])
            total_functions += len(mod.get("functions", []) or [])
            total_constants += len(mod.get("constants", []) or [])
        return {
            "classes": total_classes,
            "functions": total_functions,
            "constants": total_constants,
        }

    def _build_header(
        self,
        root_name: str,
        totals: Dict[str, int],
        files_count: int
    ) -> str:
        """Construct a short header summary line."""
        return (
            f"Project '{root_name}' summary: {files_count} file(s), "
            f"{totals['classes']} class(es), "
            f"{totals['functions']} function(s), "
            f"{totals['constants']} constant(s)."
        )

    def _group_by_package(
        self,
        modules: List[Dict[str, Any]],
        root: Optional[str]
    ) -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
        """
        Group modules by their package (directory path) under the common root.
        Returns mapping: package -> list of (filename, module_dict)
        """
        grouped: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {}
        for mod in modules:
            path = mod.get("path", "")
            rel_path = os.path.relpath(path, root) if root else path
            parts = rel_path.replace("\\", "/").split("/")
            if len(parts) > 1:
                pkg = '/'.join(parts[:-1])
            else:
                pkg = '.'  # root package
            filename = parts[-1]
            grouped.setdefault(pkg, []).append((filename, mod))
        return grouped

    def _format_tree_overview(
        self,
        grouped: Dict[str, List[Tuple[str, Dict[str, Any]]]]
    ) -> List[str]:
        """
        Create a concise tree overview of the project structure with proper
        tree symbols.
        """
        lines = ["project/"]

        # Get all packages and sort them properly
        all_packages = sorted(grouped.keys(), key=lambda p: (p != '.', p))

        # Process each package
        for i, pkg in enumerate(all_packages):
            is_last_package = i == len(all_packages) - 1

            if pkg == '.':
                # Root package files
                items = grouped[pkg]
                items = sorted(items, key=lambda x: x[0])
                for j, (filename, mod) in enumerate(items):
                    is_last_file = j == len(items) - 1
                    prefix = "└── " if is_last_file else "├── "
                    status = " (ERROR)" if mod.get("error") else ""
                    class_info = self._get_class_info_for_tree(mod)
                    lines.append(f"{prefix}{filename}{status}{class_info}")
            else:
                # Sub-packages
                pkg_parts = pkg.split('/')
                pkg_display = pkg_parts[-1]

                # Build the package line with proper tree structure
                prefix = "└── " if is_last_package else "├── "
                lines.append(f"{prefix}{pkg_display}/")

                # Get items for this package
                items = grouped[pkg]
                parent_prefix = "    " if is_last_package else "│   "

                items = sorted(items, key=lambda x: x[0])
                for j, (filename, mod) in enumerate(items):
                    is_last_file = j == len(items) - 1
                    file_prefix = "└── " if is_last_file else "├── "
                    status = " (ERROR)" if mod.get("error") else ""
                    class_info = self._get_class_info_for_tree(mod)
                    lines.append(
                        f"{parent_prefix}{file_prefix}{filename}{status}"
                        f"{class_info}"
                    )

        return lines

    def _get_class_info_for_tree(self, mod: Dict[str, Any]) -> str:
        """Get class information for tree overview display."""
        if mod.get("error"):
            return ""

        classes = mod.get("classes") or []
        if not classes:
            return ""

        # Show first few class names
        class_names = [self._name_of(c) for c in classes[:2]]
        class_str = ", ".join(class_names)
        if len(classes) > 2:
            class_str += f", +{len(classes) - 2} more"

        return f" ({class_str})"

    def _format_detailed_structure(
        self,
        grouped: Dict[str, List[Tuple[str, Dict[str, Any]]]]
    ) -> List[str]:
        """
        Format the detailed structure of the project with comprehensive
        information and tree symbols.
        """
        lines = ["project/"]

        # Get all packages and sort them properly
        all_packages = sorted(grouped.keys(), key=lambda p: (p != '.', p))

        # Process each package
        for i, pkg in enumerate(all_packages):
            is_last_package = i == len(all_packages) - 1

            items = grouped[pkg]
            t = self._compute_package_totals(items)
            class_count, func_count, const_count, error_count = t

            # Determine package display name
            pkg_display = "Root" if pkg == '.' else pkg

            # Package line with tree symbol
            pkg_prefix = "└── " if is_last_package else "├── "
            lines.append(
                f"{pkg_prefix}Package: {pkg_display} ({len(items)} modules, "
                f"{class_count} classes, {func_count} functions, "
                f"{const_count} constants)"
            )

            if error_count > 0:
                error_prefix = "    " if is_last_package else "│   "
                lines.append(
                    f"{error_prefix}    ({error_count} modules with errors)"
                )

            # Process modules in this package
            parent_prefix = "    " if is_last_package else "│   "

            items = sorted(items, key=lambda x: x[0])
            for j, (filename, mod) in enumerate(items):
                is_last_module = j == len(items) - 1
                module_prefix = "└── " if is_last_module else "├── "

                if mod.get("error"):
                    lines.append(
                        f"{parent_prefix}{module_prefix}Module: {filename}: "
                        f"ERROR: {mod.get('error')}"
                    )
                else:
                    lines.append(
                        f"{parent_prefix}{module_prefix}Module: {filename}"
                    )
                    # Format module content with proper tree symbols
                    t = ("    " if is_last_module else "│   ")
                    content_prefix = parent_prefix + t
                    lines.extend(
                        self._format_module_with_tree(
                            content_prefix, filename, mod, is_last_module
                        )
                    )

            # Add a blank line after each package except the last one
            if not is_last_package:
                lines.append("│")

        return lines

    def _format_module_with_tree(
        self,
        prefix: str,
        filename: str,
        mod: Dict[str, Any],
        is_last_module: bool
    ) -> List[str]:
        """
        Format a single module with tree symbols for all content.
        """
        lines = []
        classes = mod.get("classes") or []
        functions = mod.get("functions") or []
        constants = mod.get("constants") or []

        # Classes
        if classes:
            cls_names = ", ".join(
                self._name_of(c) for c in classes[: self.depth]
            )
            ellipsis = "..." if len(classes) > self.depth else ""
            class_prefix = "└── " if is_last_module and not functions and not constants else "├── "
            lines.append(f"{prefix}{class_prefix}Classes ({len(classes)}): {cls_names}{ellipsis}")

            for k, c in enumerate(classes[: self.depth]):
                is_last_class = k == min(len(classes), self.depth) - 1 and not functions and not constants
                class_content_prefix = prefix + ("    " if is_last_module else "│   ")
                lines.extend(self._format_class_with_tree(class_content_prefix, c, is_last_class))

        # Functions
        if functions:
            fn_names = ", ".join(self._format_function_name(f) for f in functions[: self.depth])
            ellipsis = "..." if len(functions) > self.depth else ""
            func_prefix = "└── " if is_last_module and not constants else "├── "
            lines.append(f"{prefix}{func_prefix}Functions ({len(functions)}): {fn_names}{ellipsis}")

            for k, f in enumerate(functions[: self.depth]):
                is_last_func = k == min(len(functions), self.depth) - 1 and not constants
                func_content_prefix = prefix + ("    " if is_last_module else "│   ")
                lines.append(self._format_function_brief_with_tree(func_content_prefix, f, is_last_func))

        # Constants
        if constants:
            const_names = ", ".join(str(c) for c in constants[: self.depth])
            ellipsis = "..." if len(constants) > self.depth else ""
            const_prefix = "└── "
            lines.append(f"{prefix}{const_prefix}Constants ({len(constants)}): {const_names}{ellipsis}")

        return lines

    def _format_class_with_tree(self, prefix: str, c: Any, is_last: bool) -> List[str]:
        """
        Format a class entry with tree symbols.
        """
        lines = []
        name = self._name_of(c)
        bases = self._bases_of(c)
        base_str = f" ({', '.join(bases)})" if bases else ""
        methods = self._methods_of(c)
        mcount = len(methods)
        mpreview = methods[: self.method_preview]
        mpreview_str = ", ".join(self._format_method_signature(m) for m in mpreview) or "(none)"

        class_prefix = "└── " if is_last else "├── "
        lines.append(
            f"{prefix}{class_prefix}{name}{base_str}: methods ({mcount}): {mpreview_str}{'...' if mcount > self.method_preview else ''}")

        doc = self._doc_of(c)
        if doc and self.doc_chars > 0:
            snippet = self._shorten_doc(doc)
            doc_prefix = prefix + ("    " if is_last else "│   ")
            lines.append(f"{doc_prefix}    doc: {snippet}")

        return lines

    def _format_function_brief_with_tree(self, prefix: str, f: Any, is_last: bool) -> str:
        """
        Return a single-line brief description for a function with tree symbols.
        """
        name = self._format_function_name(f)
        sig = ""
        if isinstance(f, dict):
            sig = f.get("sig", "") or ""
        sig = sig or ""

        func_prefix = "└── " if is_last else "├── "
        line = f"{prefix}{func_prefix}{name}{sig}"

        doc = f.get("doc") if isinstance(f, dict) else None
        if doc and self.doc_chars > 0:
            line += f": {self._shorten_doc(doc)}"

        return line

    def _compute_package_totals(self, items: List[Tuple[str, Dict[str, Any]]]) -> Tuple[int, int, int, int]:
        """Count classes, functions, constants, and errors for a package."""
        class_count = 0
        func_count = 0
        const_count = 0
        error_count = 0
        for filename, mod in items:
            if mod.get("error"):
                error_count += 1
                continue
            class_count += len(mod.get("classes", []) or [])
            func_count += len(mod.get("functions", []) or [])
            const_count += len(mod.get("constants", []) or [])
        return class_count, func_count, const_count, error_count

    def _format_function_name(self, f: Any) -> str:
        if isinstance(f, dict):
            return f.get("name", "<anon>")
        return str(f)

    def _format_method_signature(self, m: Any) -> str:
        """
        Return method name with signature if available.
        """
        if isinstance(m, dict):
            name = m.get("name") or "<anon>"
            sig = m.get("sig") or ""
            return f"{name}{sig}"
        return str(m)

    def _name_of(self, entry: Any) -> str:
        if isinstance(entry, dict):
            return entry.get("name") or "<anon>"
        return str(entry)

    def _bases_of(self, entry: Any) -> List[str]:
        if isinstance(entry, dict):
            b = entry.get("bases") or []
            if isinstance(b, (list, tuple)):
                return [str(x) for x in b]
            return [str(b)]
        return []

    def _methods_of(self, entry: Any) -> List[Any]:
        if isinstance(entry, dict):
            m = entry.get("methods") or []
            if isinstance(m, (list, tuple)):
                return list(m)
            return [m]
        return []

    def _doc_of(self, entry: Any) -> Optional[str]:
        if isinstance(entry, dict):
            d = entry.get("doc")
            if isinstance(d, str):
                return d.strip()
        return None

    def _shorten_doc(self, doc: str) -> str:
        """Return a single-line, whitespace-collapsed docstring truncated to doc_chars."""
        if not doc:
            return ""
        single = " ".join(doc.strip().split())
        if self.doc_chars <= 0:
            return single
        if len(single) <= self.doc_chars:
            return single
        truncated = single[: self.doc_chars].rsplit(" ", 1)[0]
        return truncated + "..."
