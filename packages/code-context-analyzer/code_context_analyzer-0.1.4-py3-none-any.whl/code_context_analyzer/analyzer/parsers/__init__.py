
from .js_parser import JSParser
from .python_parser import PythonParser

registry = {
    'py': PythonParser(),
    'js': JSParser(),
}
