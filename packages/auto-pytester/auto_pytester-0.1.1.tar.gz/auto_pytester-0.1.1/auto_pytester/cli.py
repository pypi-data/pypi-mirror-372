import argparse
from pathlib import Path
from .scanner import scan_project
from .generator import render_tests


def main():
    parser = argparse.ArgumentParser(
        prog="auto-pytest",
        description="Auto generate pytest cases from docstring YAML examples",
    )
    parser.add_argument("project_dir", type=Path, help="Root of the Python project")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output dir for tests (default: tests-auto)",
    )
    parser.add_argument(
        "--include", action="append", default=[], help="Glob to include (repeatable)"
    )
    parser.add_argument(
        "--exclude", action="append", default=[], help="Glob to exclude (repeatable)"
    )
    parser.add_argument(
        "--in-place", action="store_true", help="Generate test_xxx.py next to sources"
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    includes = args.include or ["src/**", "apps/**", "libs/**","**/*.py"]
    excludes = args.exclude or [
        "**/test_*.py",
        "tests-auto/**",
        "**/__pycache__/**",
        "**/.venv/**",
        "**/.*/**",
    ]
    root = args.project_dir.resolve()

    if args.verbose:
        print(f"[INFO] Scanning {root}")

    meta_list = list(scan_project(root, includes, excludes))
    if not meta_list:
        print("[WARN] No examples found.")
        return
    
    print(meta_list)

    render_tests(meta_list, root, in_place=args.in_place)
    if args.verbose:
        print(f"[INFO] Generated {len(meta_list)} test files.")


if __name__ == "__main__":
    main()
