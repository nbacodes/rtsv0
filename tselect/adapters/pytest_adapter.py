import re
import subprocess
from pathlib import Path
import sys


def build_pytest_command(selected_classes):
    """
    Build pytest command using -k filter instead of ::Class.
    """

    files = set()
    class_names = []

    for item in selected_classes:
        file_part, class_part = item.split("::")
        files.add(file_part)
        class_names.append(class_part)

    # Build OR filter
    k_expr = " or ".join(class_names)

    cmd = ["pytest"]

    cmd += list(files)

    k_expr = " or ".join(class_names)
    cmd += ["-k", f"({k_expr})"]


    return cmd


def execute_command(cmd):
    process = subprocess.run(
        cmd,
        text=True,
        capture_output=True
    )

    # show live output
    print(process.stdout)
    print(process.stderr)

    passed = failed = skipped = 0

    # 🔥 IMPORTANT — this must be INSIDE the function
    full_output = process.stdout + process.stderr

    summary_match = re.search(
        r"=+\s*(.*?)\s*in\s*[\d\.]+s\s*=+",
        full_output,
        re.DOTALL
    )

    if summary_match:
        summary_text = summary_match.group(1)

        passed_match = re.search(r"(\d+)\s+passed", summary_text)
        failed_match = re.search(r"(\d+)\s+failed", summary_text)
        skipped_match = re.search(r"(\d+)\s+skipped", summary_text)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        if skipped_match:
            skipped = int(skipped_match.group(1))

    return process.returncode, passed, failed, skipped
