from qwen_client import ask_qwen

from tools import list_files, read_file
from patcher import apply_patch

from models import TestResult, DebugResult, DebugPatch

import json


SYSTEM_PROMPT = """
You are a Debugger Agent.

Your job is to analyze a failed pytest result and identify
the smallest code change required to fix the application.

You will receive:

1. The original user requirement.
2. The current Python source files.
3. The pytest failure output.
4. Feedback from previous debugging attempts.

Return ONLY valid JSON.

The JSON MUST have exactly this structure:

{
    "file_to_modify": "main.py",
    "old_code": "def add(x, y):\\n    return x - y",
    "new_code": "def add(x, y):\\n    return x + y",
    "explanation": "The add function subtracts instead of adding."
}

IMPORTANT RULES:

1. Only modify application source files.

2. Never modify test files.

3. Never modify test_generated_project.py.

4. Only modify files listed in ALLOWED APPLICATION FILES.

5. Carefully inspect the actual application source code.

6. Carefully inspect the actual pytest failure.

7. Identify the actual cause of the failure.

8. The patch must fix the actual application defect.

9. Do not modify application behavior merely to make
   an incorrect test pass.

10. Do not modify tests.

11. Do not invent requirements.

12. Do not add unrelated features.

13. Do not invent functions.

14. Do not invent files.

15. Do not use filenames from earlier projects or examples.

16. Do not execute shell commands.

17. Make the smallest possible change.

18. Preserve all unrelated working code.

19. Do not rewrite the entire file unless absolutely necessary.

20. old_code MUST exactly match code currently present
    in the selected file.

21. new_code MUST contain only the replacement code.

22. new_code MUST be syntactically valid Python.

23. The resulting complete application file must remain
    valid Python.

24. Do not remove existing functionality.

25. Do not change working functions unnecessarily.

26. Do not change expected behavior simply to satisfy
    a failing test.

27. If the test itself appears incorrect, do not modify
    the test. Analyze whether a genuine application defect
    exists first.

28. Do not return corrected_code.

29. Return old_code and new_code as the targeted patch.

30. Return only JSON.

31. Do not use Markdown code fences.

32. file_to_modify MUST be exactly one of the
    ALLOWED APPLICATION FILES.

33. Do not return a file from an earlier example.

34. Do not return a test filename.

35. Do not return test_generated_project.py.

36. Before producing the patch, mentally verify that
    old_code exists exactly in the current file.

37. The patch must preserve all unrelated functions
    and classes.

38. If a patch cannot safely fix the actual application
    defect, do not invent a speculative fix.
"""
def clean_json_response(response):
    """
    Remove Markdown JSON code fences if Qwen adds them.
    """

    response = response.strip()

    if response.startswith("```json"):
        response = response[len("```json"):].strip()

    elif response.startswith("```"):
        response = response[len("```"):].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


def inspect_project():
    """
    Read Python application source files inside the
    controlled workspace.

    Test files are excluded.
    """

    files = list_files()

    project_files = []

    for filename in files:

        if (
            filename.endswith(".py")
            and not filename.startswith("test_")
        ):

            content = read_file(filename)

            project_files.append(
                {
                    "filename": filename,
                    "content": content
                }
            )

    return project_files


def analyze_failure(
    requirement,
    project_files,
    test_result,
    previous_feedback=""
):
    """
    Ask Qwen to generate a targeted debugging patch.
    """

    project_text = ""

    for project_file in project_files:

        project_text += f"""
FILE: {project_file["filename"]}

{project_file["content"]}

"""

    failure_output = test_result.stdout

    if test_result.stderr:

        failure_output += f"""

STDERR:

{test_result.stderr}
"""

    # Create an explicit list of files that the Debugger
    # is allowed to modify.
    allowed_files = ", ".join(
        project_file["filename"]
        for project_file in project_files
    )

    prompt = f"""
{SYSTEM_PROMPT}

ORIGINAL USER REQUIREMENT:

{requirement}

ALLOWED APPLICATION FILES:

{allowed_files}

CURRENT PROJECT:

{project_text}

PYTEST RESULT:

{failure_output}

PREVIOUS DEBUGGER FEEDBACK:

{previous_feedback}

IMPORTANT:

1. file_to_modify MUST be exactly one of the
   ALLOWED APPLICATION FILES listed above.

2. Do NOT invent a filename.

3. Do NOT use calculator.py unless calculator.py
   actually appears in the ALLOWED APPLICATION FILES.

4. Do NOT return the complete source file.

5. Return ONLY the smallest code patch required.

6. old_code must exactly match code currently
   present in the selected file.

7. new_code must contain only the replacement code.

8. Preserve all other functions and code.

9. explanation is optional. If you provide it,
   briefly explain why the patch fixes the failure.

Generate the debugging patch now.
"""

    response = ask_qwen(prompt)

    print("\n===== RAW DEBUGGER RESPONSE =====")
    print(response)
    print("===== END RAW DEBUGGER RESPONSE =====")

    response = clean_json_response(response)

    if not response:

        raise ValueError(
            "Debugger returned an empty response."
        )

    try:

        result = json.loads(response)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Debugger returned invalid JSON: {error}"
        )

    try:

        patch = DebugPatch.model_validate(result)

    except Exception as error:

        raise ValueError(
            f"Debugger returned an invalid patch: {error}"
        )

    return patch


def run_debugger(
    requirement,
    test_result: TestResult,
    previous_feedback=""
):
    """
    Complete Debugger workflow:

    1. Inspect source files.
    2. Read test failure.
    3. Ask Qwen for a targeted patch.
    4. Validate the patch structure.
    5. Apply only the requested change.
    6. Retry if the patch is rejected.
    """

    MAX_DEBUGGER_ATTEMPTS = 3

    if test_result.passed:

        return DebugResult(
            success=False,
            file_modified="",
            explanation=(
                "Tests already passed. "
                "Debugging was not required."
            ),
            error_analysis="No test failure."
        )

    print(
        "Debugger: inspecting project..."
    )

    project_files = inspect_project()

    if not project_files:

        raise ValueError(
            "Debugger found no Python source files."
        )

    feedback = previous_feedback

    valid_filenames = [
        project_file["filename"]
        for project_file in project_files
    ]

    for attempt in range(
        1,
        MAX_DEBUGGER_ATTEMPTS + 1
    ):

        print(
            f"\nDebugger attempt "
            f"{attempt} / {MAX_DEBUGGER_ATTEMPTS}"
        )

        try:

            print(
                "Debugger: analyzing test failure..."
            )

            patch = analyze_failure(
                requirement,
                project_files,
                test_result,
                feedback
            )

            filename = patch.file_to_modify

            # Safety check 1:
            # Never modify test files.
            if filename.startswith("test_"):

                raise ValueError(
                    "Debugger is not allowed "
                    "to modify test files."
                )

            # Safety check 2:
            # File must exist in the current project.
            if filename not in valid_filenames:

                raise ValueError(
                    f"Debugger requested an unknown file: "
                    f"{filename}"
                )

            # Safety check 3:
            # Do not allow an empty patch.
            if not patch.old_code.strip():

                raise ValueError(
                    "Debugger patch old_code is empty."
                )

            if not patch.new_code.strip():

                raise ValueError(
                    "Debugger patch new_code is empty."
                )

            # Safety check 4:
            # A patch must actually change something.
            if patch.old_code == patch.new_code:

                raise ValueError(
                    "Debugger patch does not change the code."
                )

            # --------------------------------------------------
            # Apply targeted patch
            # --------------------------------------------------

            print(
                f"Debugger: applying patch to {filename}..."
            )

            result = apply_patch(
                filename,
                patch.old_code,
                patch.new_code
            )

            print(result)

            debug_result = DebugResult(
                success=True,
                file_modified=filename,
                explanation=patch.explanation,
                error_analysis=(
                    "The Debugger analyzed the pytest "
                    "failure and generated a targeted "
                    "code patch."
                )
            )

            return debug_result

        except ValueError as error:

            print(
                f"Debugger attempt {attempt} rejected:"
            )

            print(error)

            feedback = str(error)

            if attempt == MAX_DEBUGGER_ATTEMPTS:

                raise ValueError(
                    "Debugger could not produce a valid "
                    f"patch after "
                    f"{MAX_DEBUGGER_ATTEMPTS} attempts. "
                    f"Last error: {error}"
                )

            print(
                "Debugger: sending rejection feedback "
                "back to Qwen..."
            )

    raise RuntimeError(
        "Debugger exited unexpectedly."
    )


if __name__ == "__main__":

    print(
        "Patch-based Debugger Agent "
        "loaded successfully."
    )