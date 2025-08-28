import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

tpl_cls_text = (
    files("auto_pytester.templates").joinpath("class_test_template.j2").read_text()
)
tpl_cls = Environment(
    # trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True
).from_string(tpl_cls_text)
tpl_func_text = (
    files("auto_pytester.templates").joinpath("func_test_template.j2").read_text()
)
tpl_func = Environment(
    # trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True
).from_string(tpl_func_text)


def render_tests(meta_list, root: Path, in_place: bool = False):
    """
    Generate pytest test files from parsed metadata.

    This function groups the collected test cases into two categories:

    1. **Standalone functions**
       Each function receives its own test file named
       ``test_<function_name>.py`` containing all associated test cases.

    2. **Classes**
       All methods of a class are placed into a single file named
       ``test_<class_name>.py``.
       A fixture named after the class (lowercase) is automatically provided
       to instantiate the class.

    Parameters
    ----------
    meta_list : list[dict[str, Any]]
        Metadata produced by ``scan_project``.
        Each element is a dictionary containing at least:

        * ``module``      – dotted import path to the module
        * ``qual_name``   – fully-qualified name of the callable
        * ``cls_name``    – ``None`` for standalone functions, otherwise the class name
        * ``method_name`` – ``None`` for standalone functions, otherwise the method name
        * ``examples``    – dict with ``input`` and ``expect`` keys

    root : pathlib.Path
        Root directory of the project under test.

    in_place : bool, optional
        If ``True``, test files are written adjacent to their corresponding source files.
        Otherwise, they are placed in ``<root>/tests-auto/`` (default ``False``).

    Returns
    -------
    None

    Notes
    -----
    * The generated files include a module-level docstring and follow PEP 257
      conventions for clarity.
    * All files are encoded in UTF-8.

    Examples
    --------
    >>> from pathlib import Path
    >>> from auto_pytester.scanner import scan_project
    >>> from auto_pytester.generator import render_tests
    >>> root = Path("src")
    >>> meta = list(scan_project(root, ["**/*.py"], ["**/test_*.py"]))
    >>> render_tests(meta, root, in_place=True)
    """
    buckets = defaultdict(list)
    for m in meta_list:
        key = (m["module"], m["cls_name"])
        buckets[key].append(m)

    for (module, cls_name), items in buckets.items():
        if cls_name is None:
            func_name = m["qual_name"]
            file_name = f"test_{func_name}.py"
            tpl = tpl_func
        else:
            file_name = f"test_{cls_name}.py"
            tpl = tpl_cls

        test_path = (
            (root / module.replace(".", "/")).parent / file_name
            if in_place
            else root / "tests-auto" / file_name
        )
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(tpl.render(items=items).replace("", ""), encoding="utf-8")
