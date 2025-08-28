import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict
from ..utils.decorator import timed

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

_ENVS_ = ['conftest', "class_test", "func_test"]

def get_template(tpl_name: str) -> Environment:
    """
    Load a Jinja2 template from the 'auto_pytester.templates' package.

    Parameters
    ----------
    tpl_name : str
        
        Name of the template without the '_template.j2' suffix.
        For example, 'conftest' for 'conftest_template.j2'.
    
    Returns
    --------
        jinja2.Environment object for rendering the specified template.    
    """
    tpl_text = files("auto_pytester.templates").joinpath(f"{tpl_name}_template.j2").read_text()
    return Environment(
        # trim_blocks=True, 
        # lstrip_blocks=True, 
        # keep_trailing_newline=True
    ).from_string(tpl_text)

tpl_conftest = get_template('conftest')
tpl_cls = get_template('class_test')
tpl_func = get_template('func_test')


@timed(unit="ms")
def render_tests(meta_list: list, output_dir: Path)->None:
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

    output_dir : pathlib.Path
        Directory where the generated test files will be saved.
        If the directory does not exist, it will be created.

    Returns
    -------
    None

    Notes
    -----
    * The generated files include a module-level docstring and follow PEP 257
      conventions for clarity.
    * All files are encoded in UTF-8.
    """

    conftest_path =  output_dir / "conftest.py"
    conftest_path.parent.mkdir(parents=True, exist_ok=True)
    conftest_path.write_text(tpl_conftest.render(), encoding="utf-8")

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

        """
        if args.in_place:
             test_path = (root / module.replace(".", "/")).parent / file_name
        """

        test_path =  output_dir / file_name
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(tpl.render(items=items), encoding="utf-8")
