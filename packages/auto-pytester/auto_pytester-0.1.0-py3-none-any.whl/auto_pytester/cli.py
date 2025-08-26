import argparse, pathlib
from .scanner import scan_project
from .generator import render_tests

def main():
    parser = argparse.ArgumentParser(
        prog="auto-pytest",
        description="扫描项目并自动生成 pytest 用例"
    )
    parser.add_argument("project_dir", type=pathlib.Path,
                        help="要扫描的 Python 项目根目录")
    parser.add_argument("-o", "--output-dir", type=pathlib.Path,
                        default=pathlib.Path("tests-auto"),
                        help="生成测试文件存放目录 (默认 tests-auto)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="打印详细日志")
    args = parser.parse_args()

    if args.verbose:
        print(f"[INFO] 开始扫描 {args.project_dir}")

    # 1. 扫描
    meta_list = list(scan_project(args.project_dir))
    if not meta_list:
        print("[WARN] 未找到任何带示例的函数")
        return

    # 2. 生成
    # print(meta_list)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    render_tests(meta_list, args.output_dir)

    if args.verbose:
        print(f"[INFO] 共生成 {len(meta_list)} 个测试文件 → {args.output_dir}")

if __name__ == "__main__":
    main()