import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from collections import defaultdict

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

tpl_text = (
    files("auto_pytester.templates").joinpath("class_test_template.j2").read_text()
)
tpl_cls = Environment().from_string(tpl_text)
tpl_text = (
    files("auto_pytester.templates").joinpath("func_test_template.j2").read_text()
)
tpl_func = Environment().from_string(tpl_text)


def render_tests(
    meta_list, root: Path, in_place: bool = False, classmethod: bool = False
):
    buckets = defaultdict(list)
    for m in meta_list:
        key = (m["module"], m["cls_name"])   # 独立函数 cls_name=None
        buckets[key].append(m)

    for (module, cls_name), items in buckets.items():
        if cls_name is None:
            # 独立函数：test_<函数名>.py
            func_name = m["qual_name"]
            file_name = f"test_{func_name}.py"
            tpl = tpl_func
        else:
            # 类：test_<类名>.py
            file_name = f"test_{cls_name}.py"
            tpl = tpl_cls

        test_path = (root / module.replace(".", "/")).parent / file_name if in_place \
                    else root / "tests-auto" / file_name
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(tpl.render(items=items), encoding="utf-8")
