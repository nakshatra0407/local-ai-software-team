from pathlib import Path
import subprocess
import sys

from models import TestResult


WORKSPACE = Path("workspace").resolve()


def run_tests():

    if not WORKSPACE.is_dir():
        raise FileNotFoundError(
            f"Workspace not found: {WORKSPACE}"
        )

    command = [
        sys.executable,
        "-m",
        "pytest",
        str(WORKSPACE),
        "-v"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=WORKSPACE
    )

    return TestResult(
        passed=(result.returncode == 0),
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr
    )


if __name__ == "__main__":

    result = run_tests()

    print("TEST RESULT:")
    print(result.model_dump())