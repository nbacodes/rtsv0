import argparse
import time
from pathlib import Path

from tselect.utils.loader import load_yaml, load_json
from tselect.core.selector import map_files_to_components, collect_tests_from_components
from tselect.adapters.pytest_adapter import build_pytest_command, execute_command
from tselect.reporting.summary import generate_summary
from tselect.reporting.cache import load_cache, save_cache
from tselect.adapters.baseline_detector import detect_baseline_command


def pretty_print_command(cmd, hint):
    print("\n=== TSELECT COMMAND ===\n")

    # remove "python -m pytest"
    pytest_parts = cmd[3:] if len(cmd) > 3 else cmd

    print("pytest \\")
    for part in pytest_parts:
        print(f"  {part} \\")

    print("\nTo execute:")
    print(hint)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="tselect",
        description="Selective test runner"
    )

    subparsers = parser.add_subparsers(dest="command")

    # ---- run command ----
    run_parser = subparsers.add_parser("run", help="Select tests to run")

    run_parser.add_argument(
        "--changed",
        nargs="+",
        required=True,
        help="List of changed files"
    )

    run_parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute selected tests"
    )

    # ---- baseline command ----
    baseline_parser = subparsers.add_parser(
        "baseline",
        help="Create baseline timing"
    )

    baseline_parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute baseline tests"
    )

    args = parser.parse_args()

    # ==========================================================
    # RUN COMMAND
    # ==========================================================
    if args.command == "run":

        repo_root = Path.cwd()

        ownership_path = repo_root / "ownership.yaml"
        json_path = repo_root / "config" / "testSuiteTorchInductor.json"

        cache = load_cache(repo_root)
        baseline_time = cache.get("baseline_time")

        ownership = load_yaml(ownership_path)
        test_json = load_json(json_path)

        components = map_files_to_components(args.changed, ownership)

        print("Affected components:", components)

        selected_classes, class_test_count = collect_tests_from_components(
            components,
            test_json
        )

        print("\nSelected classes:")
        for cls in selected_classes:
            print("-", cls)

        total_tests = sum(class_test_count.values())
        print(f"\nTotal tests inside classes: {total_tests}")

        cmd = build_pytest_command(list(selected_classes))

        pretty_print_command(cmd, "tselect run --changed <files> --execute")

        if args.execute:
            start_time = time.time()
            return_code = execute_command(cmd)
            duration = time.time() - start_time

            if baseline_time is None:
                print("\nNo baseline found — saving this run as baseline.")
                cache["baseline_time"] = duration
                save_cache(repo_root, cache)
                baseline_time = duration

            generate_summary(
                components=components,
                total_tests=total_tests,
                duration=duration,
                status="PASSED" if return_code == 0 else "FAILED",
                baseline=baseline_time,
            )

    # ==========================================================
    # BASELINE COMMAND
    # ==========================================================
    elif args.command == "baseline":

        from pathlib import Path
        import time
        from tselect.adapters.baseline_detector import detect_baseline_command

        repo_root = Path.cwd()

        cmd = detect_baseline_command(repo_root)

        print("\n=== BASELINE COMMAND ===")
        print(" ".join(cmd))

        start_time = time.time()
        return_code = execute_command(cmd)
        duration = time.time() - start_time

        cache = load_cache(repo_root) or {}
        cache["baseline_time"] = duration
        save_cache(repo_root, cache)

        print(f"\nBaseline recorded: {duration:.2f}s")


    else:
        parser.print_help()
