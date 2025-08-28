import argparse
from pathlib import Path
from .src.scanner import scan_project
from .src.generator import render_tests


def main():
    parser = argparse.ArgumentParser(
        prog="auto-pytest",
        description="Auto generate pytest cases from docstring YAML examples",
    )
    parser.add_argument(
        "project_dir", 
        type=Path, 
        help="Root of the Python project"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=None,
        help="Output dir for tests (default: tests-auto)",
    )
    parser.add_argument(
        "-i",
        "--include", 
        action="append",
        default=[], 
        help="Glob to include (repeatable)"
    )
    parser.add_argument(
        "-e",
        "--exclude", 
        action="append", 
        default=[], 
        help="Glob to exclude (repeatable)"
    )
    parser.add_argument(
        "-I",
        "--inplace",
        action="store_true", 
        help="Generate test_xxx.py next to sources"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Show verbose output"
    )
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
    
    # print(meta_list)
    output_dir = args.output_dir or (root / "tests-auto")

    render_tests(meta_list, output_dir)
    if args.verbose:
        print(f"[INFO] Generated {len(meta_list)} test cases in {output_dir}")


if __name__ == "__main__":
    main()
