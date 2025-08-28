import ast
import re
import textwrap
import yaml
from pathlib import Path
from typing import List, Iterator, Dict, Any

BLOCK_RE = re.compile(r">>>(.*?)<<<", re.DOTALL)
IO_RE = re.compile(r"^(.*?)input:(.*?)output:(.*?)$", re.DOTALL)


def iter_python_files(
    root: Path, includes: List[str], excludes: List[str]
) -> Iterator[Path]:
    import fnmatch

    for pat in includes:
        for py in root.glob(pat):
            if py.is_file() and py.suffix == ".py":
                if any(fnmatch.fnmatch(str(py), exc) for exc in excludes):
                    continue
                yield py


def module_import_path(project_root: Path, py_file: Path) -> str:
    rel = py_file.relative_to(project_root).with_suffix("")
    parts = rel.parts
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def extract_examples(doc: str) -> Iterator[Dict[str, Any]]:
    for block in BLOCK_RE.findall(doc):
        m = IO_RE.search(textwrap.dedent(block).strip())
        if not m:
            continue
        case_name = yaml.safe_load(textwrap.dedent(m.group(1)))
        inp = yaml.safe_load(textwrap.dedent(m.group(2)))
        exp = yaml.safe_load(textwrap.dedent(m.group(3)))
        yield {"case_name": case_name, "input": inp, "expect": exp}


def scan_project(root: Path, includes: List[str], excludes: List[str]) -> Iterator[Dict[str, Any]]:
    for py_file in iter_python_files(root, includes, excludes):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        mod_path = module_import_path(root, py_file)

        # 先收集所有类
        classes = {n: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

        # 1) 类方法
        for cls_node in classes.values():
            cls_name = cls_node.name
            for method in ast.walk(cls_node):
                if isinstance(method, ast.FunctionDef):
                    for ex in extract_examples(ast.get_docstring(method) or ""):
                        yield {
                            "module": mod_path,
                            "qual_name": f"{cls_name}.{method.name}",
                            "is_method": True,
                            "cls_name": cls_name,
                            "method_name": method.name,
                            "examples": ex,
                        }

        # 2) 顶层独立函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node not in (
                m for c in classes.values() for m in ast.walk(c) if isinstance(m, ast.FunctionDef)
            ):
                for ex in extract_examples(ast.get_docstring(node) or ""):
                    yield {
                        "module": mod_path,
                        "qual_name": node.name,
                        "is_method": False,
                        "cls_name": None,
                        "method_name": None,
                        "examples": ex,
                    }