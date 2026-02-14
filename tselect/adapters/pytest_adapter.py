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

    cmd = [sys.executable, "-m", "pytest"]

    cmd += list(files)

    k_expr = " or ".join(class_names)
    cmd += ["-k", f"({k_expr})"]


    return cmd


def execute_command(cmd):
    result = subprocess.run(cmd)
    return result.returncode
