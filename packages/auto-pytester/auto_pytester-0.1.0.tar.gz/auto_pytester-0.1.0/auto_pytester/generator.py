from jinja2 import Template
import pathlib

import sys

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

template_content = None

tpl_text = files("auto_pytester.templates").joinpath("test_template.j2").read_text()


tpl = Template(tpl_text)


def render_tests(meta_list, output_dir):
    for meta in meta_list:
        test_code = tpl.render(meta)
        test_file = (
            pathlib.Path(output_dir)
            / f"test_{meta['module_name']}_{meta['func']}.py"
        )
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(test_code)
