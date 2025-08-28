import ast, sys
import re
import textwrap
import yaml, json
from pathlib import Path
from typing import List, Iterator, Dict, Any
from ..utils.decorator import timed

BLOCK_RE = re.compile(r">>> (\w+)\n(.*?)<<<", re.DOTALL)

PARSERS = {
    "yaml": yaml.safe_load,
    "json": json.loads,
    "toml": None,  # use tomllib.loads if Python ≥3.11, else tomli.loads.
}

if sys.version_info >= (3, 11):
    import tomllib

    PARSERS["toml"] = tomllib.loads
else:
    import tomli

    PARSERS["toml"] = tomli.loads

IO_RE = re.compile(r"^doc:(.*?)input:(.*?)output:(.*?)$", re.DOTALL)


def iter_python_files(
    root: Path, includes: List[str], excludes: List[str]
) -> Iterator[Path]:
    """
    Recursively yield Python source files within *root* according to
    inclusion and exclusion glob patterns.

    Parameters
    ----------
    root : pathlib.Path
        Base directory to start the search.
    includes : list[str]
        Glob patterns of files to include (e.g. ``["src/**/*.py"]``).
    excludes : list[str]
        Glob patterns of files or directories to ignore (e.g.
        ``["**/test_*.py", "**/.venv/**"]``).

    Yields
    ------
    pathlib.Path
        Absolute paths of ***.py** files that match *includes* and do
        **not** match *excludes*.

    Notes
    -----
    * Patterns are applied in the order provided; later patterns do
      **not** override earlier ones.
    * Directory exclusion is applied **before** file matching to avoid
      scanning large subtrees (e.g. ``.venv``).
    """
    import fnmatch

    for pat in includes:
        for py in root.glob(pat):
            if py.is_file() and py.suffix == ".py":
                if any(fnmatch.fnmatch(str(py), exc) for exc in excludes):
                    continue
                yield py


def module_import_path(project_root: Path, py_file: Path) -> str:
    """
    Convert a filesystem path into a Python importable dotted name.

    Parameters
    ----------
    project_root : pathlib.Path
        The base directory used as the package root.
    py_file : pathlib.Path
        Absolute or relative path to the Python source file.

    Returns
    -------
    str
        Dotted module name, e.g.::

            Path("src/foo/bar.py") -> "src.foo.bar"
            Path("src/foo/__init__.py") -> "src.foo"
    """
    rel = py_file.relative_to(project_root).with_suffix("")
    parts = rel.parts
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def extract_examples(doc: str) -> Iterator[Dict[str, Any]]:
    """
    Extract YAML examples from a docstring.

    Expected docstring format::

        Examples:
        >>> yaml
        doc: add two numbers
        input:
            a: 2
            b: 3
        output: 5
        <<<

    Parameters
    ----------
    doc : str
        The docstring in which to look for YAML blocks.

    Yields
    ------
    dict[str, Any]
        Dictionary with keys:

        - case_name : str | None
            Optional test case description.
        - input : dict
            Positional/keyword arguments to pass to the callable.
        - expect : Any
            Expected return value or exception name.
    """
    # for block in BLOCK_RE.findall(doc):
    #     m = IO_RE.search(textwrap.dedent(block).strip())
    #     if not m:
    #         continue
    #     case_name = yaml.safe_load(textwrap.dedent(m.group(1)))
    #     inp = yaml.safe_load(textwrap.dedent(m.group(2)))
    #     exp = yaml.safe_load(textwrap.dedent(m.group(3)))
    #     yield {"case_name": case_name, "input": inp, "expect": exp}

    for identifier, body in BLOCK_RE.findall(doc):
        parser = PARSERS.get(identifier.lower())
        if parser is None:
            continue
        data = parser(textwrap.dedent(body))
        yield {
            "doc": data.get("doc"),
            "input": data["input"],
            "expect": data["output"] if identifier.lower() !='toml' else data["output"]['value'],
        }

@timed(unit="ms")
def scan_project(
    root: Path, includes: List[str], excludes: List[str]
) -> Iterator[Dict[str, Any]]:
    """
    Scan a Python project and yield test-case metadata.

    The function walks the specified source tree, identifies
    * standalone functions* and *class methods*, extracts YAML
    examples embedded in their docstrings, and returns structured
    metadata for downstream test generation.

    Parameters
    ----------
    root : pathlib.Path
        Root directory of the project to scan.
    includes : list[str]
        Glob patterns for files to include (e.g. ["src/**/*.py"]).
    excludes : list[str]
        Glob patterns for files or directories to ignore
        (e.g. ["**/test_*.py", "**/.venv/**"]).

    Yields
    ------
    dict[str, Any]
        A metadata dictionary for each discovered test case:

        - module        : dotted import path (e.g. "src.calc")
        - qual_name     : fully-qualified callable name
        - is_method     : True for class methods, False otherwise
        - cls_name      : class name (None for standalone functions)
        - method_name   : method name (None for standalone functions)
        - examples      : dict with "input" and "expect" keys parsed
                          from docstring YAML examples

    Notes
    -----
    * Only `.py` files are processed.
    * Nested classes are supported; their methods are collected
      under the innermost class name.
    * Functions or methods without docstring examples are skipped.
    """
    # for py_file in iter_python_files(root, includes, excludes):
    #     tree = ast.parse(py_file.read_text(encoding="utf-8"))
    #     mod_path = module_import_path(root, py_file)

    #     classes = {n: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

    #     for cls_node in classes.values():
    #         cls_name = cls_node.name
    #         for method in ast.walk(cls_node):
    #             if isinstance(method, ast.FunctionDef):
    #                 for ex in extract_examples(ast.get_docstring(method) or ""):
    #                     yield {
    #                         "module": mod_path,
    #                         "qual_name": f"{cls_name}.{method.name}",
    #                         "is_method": True,
    #                         "cls_name": cls_name,
    #                         "method_name": method.name,
    #                         "examples": ex,
    #                     }

    #     for node in ast.walk(tree):
    #         if isinstance(node, ast.FunctionDef) and node not in (
    #             m
    #             for c in classes.values()
    #             for m in ast.walk(c)
    #             if isinstance(m, ast.FunctionDef)
    #         ):
    #             for ex in extract_examples(ast.get_docstring(node) or ""):
    #                 yield {
    #                     "module": mod_path,
    #                     "qual_name": node.name,
    #                     "is_method": False,
    #                     "cls_name": None,
    #                     "method_name": None,
    #                     "examples": ex,
    #                 }
    for py_file in iter_python_files(root, includes, excludes):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        mod_path = module_import_path(root, py_file)

        class_methods = set()
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        for cls in classes:
            cls_name = cls.name
            for method in ast.walk(cls):
                if isinstance(method, ast.FunctionDef):
                    class_methods.add(id(method))
                    for ex in extract_examples(ast.get_docstring(method) or ""):
                        yield {
                            "module": mod_path,
                            "qual_name": f"{cls_name}.{method.name}",
                            "is_method": True,
                            "cls_name": cls_name,
                            "method_name": method.name,
                            "examples": ex,
                        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and id(node) not in class_methods:
                for ex in extract_examples(ast.get_docstring(node) or ""):
                    yield {
                        "module": mod_path,
                        "qual_name": node.name,
                        "is_method": False,
                        "cls_name": None,
                        "method_name": None,
                        "examples": ex,
                    }