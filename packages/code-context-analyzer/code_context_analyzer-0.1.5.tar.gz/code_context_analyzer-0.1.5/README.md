# Code Context Analyzer

> Analyze the structural context of codebases with file discovery, parsing, summarization, and CLI support.

**Code Context Analyzer** is a Python tool that inspects a codebase (local or GitHub) and provides a structured summary of its layout — including modules, classes, functions, and constants — with support for Python and JavaScript.

---

## 🔧 Features

- 📁 **Codebase discovery** with `.gitignore` respect
- 🧠 **Parsers for Python and JavaScript**
- 📋 **Clipboard export**
- 🖨️ **CLI output formatting** with depth and hierarchy controls
- 🌐 **Supports local paths or GitHub URLs**
- 🧪 **Extensible parser architecture**

---

## 🚀 Installation

```bash
pip install code-context-analyzer
```
Or clone it with 
```bash
git clone https://github.com/youruser/code-context-analyzer.git
cd code-context-analyzer
pip install .
```

## 🧪 Example Usage
```bash
cca ./my_project --lang python --depth 3
```
Or
```bash
cca https://github.com/pallets/flask --lang python --depth 2
```

## 📦 Used configurable flags
| Flag  |                    Description |
|:------|:--------------------------:|
| --lang | Comma-separated list of languages (e.g. python,js) |
| --depth   |      How deep the hierarchy output should go |
| --max-files |  Optional limit on files to analyze                          |
|--ignore-tests|Skip test files|
|--copy|Copy output to clipboard|

## 🧩 Architecture Overview
```bash
code_context_analyzer/
├── cli/
│   ├── __init__.py            # CLI app codes
├── analyzer/
│   ├── discovery.py          # File discovery logic
│   ├── formatter.py          # Output formatter
│   ├── repository_handler.py # GitHub/local repo handling
│   ├── clipboard.py          # Clipboard support
│   ├── parsers/              # Code parsers (Python, JS)
│   └── utils/                # Temporary directory helpers
└── tests/                    # Test suite
└── main.py                   # Entrypoint
```

## 🛠️ Development
Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```
Run tests:
```bash
pytest
```

## 📚 Documentation
Generated using MkDocs
. Run locally:
```bash
pip install mkdocs
mkdocs serve
```

## 🪪 License
MIT License © **Md. Ahasanul Arafath**
