from pathlib import Path
import ast

from qwen_client import ask_qwen
from test_runner import run_tests
from tools import create_file, edit_file


WORKSPACE = Path("workspace").resolve()

MAX_TEST_GENERATION_ATTEMPTS = 3


# =========================================================
# PROJECT INSPECTION
# =========================================================

def inspect_project():
    """
    Find the current generated application.

    Test generation is based ONLY on the current workspace.
    """

    if not WORKSPACE.is_dir():
        raise FileNotFoundError(
            f"Workspace not found: {WORKSPACE}"
        )

    application_files = []

    for file_path in WORKSPACE.glob("*.py"):

        if file_path.name.startswith("test_"):
            continue

        application_files.append(file_path)

    if not application_files:
        raise FileNotFoundError(
            "No application Python file found in workspace."
        )

    project_files = {}

    for file_path in application_files:

        project_files[file_path.name] = (
            file_path.read_text(
                encoding="utf-8"
            )
        )

    return project_files


# =========================================================
# APPLICATION ANALYSIS
# =========================================================

def inspect_application(code):

    try:
        tree = ast.parse(code)

    except SyntaxError as error:
        raise ValueError(
            f"Application contains invalid Python syntax: {error}"
        )

    functions = []
    classes = {}

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):
            functions.append(node.name)

        elif isinstance(node, ast.ClassDef):

            methods = []

            for child in node.body:

                if isinstance(
                    child,
                    (
                        ast.FunctionDef,
                        ast.AsyncFunctionDef
                    )
                ):
                    methods.append(child.name)

            classes[node.name] = methods

    return {
        "functions": functions,
        "classes": classes
    }


# =========================================================
# SYNTAX VALIDATION
# =========================================================

def validate_test_syntax(test_code):

    try:
        ast.parse(test_code)

    except SyntaxError as error:

        raise ValueError(
            "Generated tests contain invalid Python syntax: "
            f"{error}"
        )


# =========================================================
# TEST STRUCTURE
# =========================================================

def validate_test_structure(test_code):

    tree = ast.parse(test_code)

    tests = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith("test_")
    ]

    if not tests:

        raise ValueError(
            "Testing Agent did not generate pytest test functions."
        )


# =========================================================
# IMPORT VALIDATION
# =========================================================

def validate_imports(
    test_code,
    application_files
):
    """
    Validate that:

    - pytest is imported when pytest is used
    - current application is imported
    """

    tree = ast.parse(test_code)

    application_modules = {
        Path(filename).stem
        for filename in application_files
    }

    imported_modules = set()

    pytest_imported = False
    pytest_used = False

    for node in ast.walk(tree):

        # ---------------------------------------------
        # import something
        # ---------------------------------------------

        if isinstance(node, ast.Import):

            for alias in node.names:

                if alias.name in application_modules:
                    imported_modules.add(
                        alias.name
                    )

                if alias.name == "pytest":
                    pytest_imported = True

        # ---------------------------------------------
        # from something import ...
        # ---------------------------------------------

        elif isinstance(node, ast.ImportFrom):

            if node.module in application_modules:
                imported_modules.add(
                    node.module
                )

            if node.module == "pytest":
                pytest_imported = True

        # ---------------------------------------------
        # detect pytest usage
        # ---------------------------------------------

        elif isinstance(node, ast.Name):

            if node.id == "pytest":
                pytest_used = True

        elif isinstance(node, ast.Attribute):

            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "pytest"
            ):
                pytest_used = True

    if not imported_modules:

        raise ValueError(
            "Tests do not import the actual generated application."
        )

    if pytest_used and not pytest_imported:

        raise ValueError(
            "Tests use pytest but do not import pytest."
        )


# =========================================================
# BAD PATTERN VALIDATION
# =========================================================

def validate_bad_patterns(test_code):

    bad_patterns = [
        "sys.stdout.getvalue()",
        "stdout.getvalue()",
        "expected_output.txt"
    ]

    for pattern in bad_patterns:

        if pattern in test_code:

            raise ValueError(
                f"Invalid testing pattern detected: {pattern}. "
                "Use pytest capsys for printed output."
            )


# =========================================================
# PREVIOUS PROJECT CONTAMINATION
# =========================================================

def validate_project_scope(
    test_code,
    requirement
):

    test_lower = test_code.lower()
    requirement_lower = requirement.lower()

    unrelated_terms = [
        "calculator",
        "calculator_app",
        "addition",
        "subtraction",
        "expense_tracker",
        "password_generator",
        "weather_app"
    ]

    for term in unrelated_terms:

        if (
            term in test_lower
            and term not in requirement_lower
        ):

            raise ValueError(
                "Tests contain unrelated previous-project "
                f"functionality: {term}"
            )


# =========================================================
# SAVE TEST FILE
# =========================================================

def save_test_file(test_code):

    filename = "test_generated_project.py"

    test_path = WORKSPACE / filename

    if test_path.exists():

        edit_file(
            filename,
            test_code
        )

    else:

        create_file(
            filename,
            test_code
        )

    return filename


# =========================================================
# TESTING PROMPT
# =========================================================

def build_testing_prompt(
    requirement,
    project_files
):

    application_text = ""
    interface_text = ""

    for filename, code in project_files.items():

        analysis = inspect_application(code)

        application_text += f"""
==================================================
APPLICATION FILE
==================================================

{filename}

{code}
"""

        interface_text += f"""
==================================================
ACTUAL INTERFACE
==================================================

File: {filename}

Functions:
{analysis["functions"]}

Classes:
{analysis["classes"]}
"""

    return f"""
You are the Testing Agent.

Generate ONE complete pytest test file for the CURRENT
software project.

==================================================
CURRENT USER REQUIREMENT
==================================================

{requirement}

==================================================
ACTUAL APPLICATION CODE
==================================================

{application_text}

==================================================
ACTUAL APPLICATION INTERFACE
==================================================

{interface_text}

==================================================
CRITICAL INSTRUCTION
==================================================

The application code above is the source of truth.

Do NOT invent functions.

Do NOT invent classes.

Do NOT invent global variables.

Do NOT invent return values.

Do NOT invent data structures.

Use the functions/classes EXACTLY as they appear above.

==================================================
REQUIRED TEST FILE FORMAT
==================================================

Your response MUST start with:

import pytest

and then import the current application.

For example:

from simple_to_do_list import (
    Task,
    add_task,
    remove_task,
    list_tasks,
    mark_task_as_completed
)

ONLY use names that actually exist in the application.

Then create pytest functions:

def test_add_task():
    ...

def test_remove_task():
    ...

def test_list_tasks():
    ...

def test_mark_task_as_completed():
    ...

Adapt these tests to the ACTUAL application interface.

==================================================
TESTING RULES
==================================================

1. Test only the current user requirement.

2. Do not test calculator functionality.

3. Do not test previous projects.

4. Do not assume a global variable called "tasks".

5. If the application requires a tasks list argument,
   create the list inside the test.

6. If the application uses a Task class,
   use the actual Task class.

7. If remove_task removes an item, verify that the item
   was removed.

8. Removing a task must NOT be treated as completing
   another task.

9. If mark_task_as_completed changes a completion state,
   test that actual state.

10. If list_tasks prints output, use capsys.

Example:

def test_list_tasks(capsys):
    ...
    list_tasks(tasks)
    captured = capsys.readouterr()
    assert "Task name" in captured.out

11. Never use:

sys.stdout.getvalue()

12. Never create expected_output.txt.

13. If pytest.raises is used, pytest is already imported
    at the top.

14. Every test must be valid standalone pytest code.

15. Do not write explanations.

16. Do not use Markdown code fences.

17. Return ONLY Python code.

==================================================
IMPORTANT
==================================================

Do NOT blindly copy the example tests.

Read the ACTUAL APPLICATION CODE first.

Use its actual function signatures and behavior.

Generate the complete test file now.
"""


# =========================================================
# TESTING AGENT
# =========================================================

def run_testing_agent(requirement):

    project_files = inspect_project()

    prompt = build_testing_prompt(
        requirement,
        project_files
    )

    last_error = None

    for attempt in range(
        1,
        MAX_TEST_GENERATION_ATTEMPTS + 1
    ):

        print(
            f"\nTesting Agent attempt "
            f"{attempt} / {MAX_TEST_GENERATION_ATTEMPTS}"
        )

        response = ask_qwen(prompt)

        if not response.strip():

            last_error = ValueError(
                "Testing Agent returned an empty response."
            )

            continue

        test_code = response.strip()

        # -------------------------------------------------
        # Remove Markdown
        # -------------------------------------------------

        if test_code.startswith("```python"):

            test_code = test_code[
                len("```python"):
            ].strip()

        elif test_code.startswith("```"):

            test_code = test_code[
                len("```"):
            ].strip()

        if test_code.endswith("```"):

            test_code = test_code[
                :-3
            ].strip()

        try:

            # ---------------------------------------------
            # Validate generated tests
            # ---------------------------------------------

            validate_test_syntax(
                test_code
            )

            validate_test_structure(
                test_code
            )

            validate_imports(
                test_code,
                project_files.keys()
            )

            validate_bad_patterns(
                test_code
            )

            validate_project_scope(
                test_code,
                requirement
            )

            # ---------------------------------------------
            # Save
            # ---------------------------------------------

            save_test_file(
                test_code
            )

            # ---------------------------------------------
            # Run pytest
            # ---------------------------------------------

            result = run_tests()

            print(
                result.stdout
            )

            if result.stderr:
                print(
                    result.stderr
                )

            # ---------------------------------------------
            # Tests passed
            # ---------------------------------------------

            if result.passed:

                print(
                    "Testing Agent: tests passed."
                )

                return result

            # ---------------------------------------------
            # Tests failed
            # ---------------------------------------------

            last_error = ValueError(
                "Generated tests failed."
            )

            prompt = f"""
{prompt}

==================================================
PREVIOUS TEST RUN FAILED
==================================================

PYTEST OUTPUT:

{result.stdout}

{result.stderr}

==================================================
FIX THE TEST FILE
==================================================

Inspect the actual application code again.

Do not assume the application is wrong.

Correct any test that uses:

- nonexistent functions
- nonexistent variables
- incorrect arguments
- incorrect return values
- incorrect data structures
- incorrect behavior

For printed output, use:

captured = capsys.readouterr()

Do not use sys.stdout.getvalue().

For pytest.raises, pytest must be imported.

Return ONLY the complete corrected pytest file.
"""

        except Exception as error:

            print(
                f"Testing Agent attempt {attempt} rejected:"
            )

            print(error)

            last_error = error

            prompt = f"""
{prompt}

==================================================
VALIDATION ERROR
==================================================

{error}

Generate a COMPLETE corrected pytest file.

Remember:

import pytest

must appear at the top.

The current application must be imported.

Only use functions/classes that actually exist.

Do not invent global application state.

Do not use sys.stdout.getvalue().

Use capsys for printed output.

Return ONLY Python code.
"""

    raise RuntimeError(
        "Testing Agent failed after "
        f"{MAX_TEST_GENERATION_ATTEMPTS} attempts. "
        f"Last error: {last_error}"
    )


if __name__ == "__main__":

    requirement = """
    Create a Python program that manages a simple to-do list.
    It should allow adding a task, removing a task,
    listing all tasks, and marking a task as completed.
    Store the tasks in memory using a Python list.
    """

    result = run_testing_agent(
        requirement
    )

    print(
        "\n=============================="
    )

    print(
        "TESTING RESULT"
    )

    print(
        "=============================="
    )

    print(
        f"Passed: {result.passed}"
    )

    print(
        f"Exit code: {result.exit_code}"
    )