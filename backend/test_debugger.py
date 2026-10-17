import sys

sys.path.insert(0, "backend")

from debugger import run_debugger
from test_runner import run_tests


requirement = """
Create a simple Python calculator program with
functions for addition and subtraction.
"""


print("Running tests before debugging...")

test_result = run_tests()

print("\n===== BEFORE DEBUGGING =====")
print(test_result.model_dump())


if not test_result.passed:

    print("\nRunning Debugger...")

    debug_result = run_debugger(
        requirement,
        test_result
    )

    print("\n===== DEBUGGER RESULT =====")
    print(debug_result.model_dump())

else:

    print("Tests already pass. Debugging is not required.")