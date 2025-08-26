import ast, yaml, re, pathlib
import re, textwrap, yaml

# 1. 先匹配整个示例块
BLOCK_RE = re.compile(r">>> yaml(.*?)<<<", re.DOTALL)

# 2. 在每个块里再切 input / output
IO_RE = re.compile(r"^input:(.*?)output:(.*?)$", re.DOTALL)


def extract_examples(doc: str):
    res = []
    for block in BLOCK_RE.findall(doc):
        io_match = IO_RE.search(textwrap.dedent(block).strip())
        if not io_match:
            continue
        inp_yaml, out_yaml = io_match.groups()
        res.append(
            {
                "input": yaml.safe_load(textwrap.dedent(inp_yaml)),
                "output": yaml.safe_load(textwrap.dedent(out_yaml)),
            }
        )
    return res


def scan_project(root: pathlib.Path):
    for py_file in root.rglob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                examples = extract_examples(ast.get_docstring(node))
                yield dict(
                    module_path=str(py_file.relative_to(root.parent)).replace(".py", ""),
                    module_name=str(py_file.name).replace(".py", ""),
                    func=node.name,
                    args=[a.arg for a in node.args.args],
                    examples=examples,
                )
