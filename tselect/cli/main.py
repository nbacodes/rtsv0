import argparse
from tselect.utils.loader import load_yaml, load_json
from tselect.core.selector import map_files_to_components, collect_tests_from_components
from tselect.adapters.pytest_adapter import build_pytest_command, execute_command
import time
from tselect.reporting.summary import generate_summary
from tselect.reporting.cache import load_cache, save_cache

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

    args = parser.parse_args()

    # Temporary debug output
    if args.command == "run":

        from pathlib import Path

        repo_root = Path.cwd()

        ownership_path = repo_root / "ownership.yaml"
        json_path = repo_root / "config" / "testSuiteTorchInductor.json"

        repo_root = Path.cwd()

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

        if not selected_classes:
            print("\nNo classes selected — falling back to full test suite.")

        cmd = build_pytest_command(list(selected_classes))

        print("\nCommand:")
        print(" ".join(cmd))

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

    else:
        parser.print_help()
    
    
