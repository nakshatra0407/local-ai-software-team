from pathlib import Path

from state import ProjectState
from project_manager import analyze_requirement
from architect import design_project
from coding_agent import generate_code
from tools import create_file
from testing_agent import run_testing_agent
from test_runner import run_tests
from debugger import run_debugger


MAX_DEBUG_ITERATIONS = 3

WORKSPACE = Path("workspace").resolve()


def prepare_workspace():
    """
    Prepare a clean workspace for a new generated project.

    Only files and folders inside the controlled workspace
    are removed.

    The workspace directory itself is preserved.
    """

    if not WORKSPACE.is_dir():
        WORKSPACE.mkdir(
            parents=True,
            exist_ok=True
        )

    print(
        f"Preparing workspace: {WORKSPACE}"
    )

    for item in WORKSPACE.iterdir():

        if item.is_dir():

            # Remove generated directories such as
            # __pycache__ and .pytest_cache.
            import shutil

            shutil.rmtree(
                item
            )

        else:

            item.unlink()

    print(
        "Workspace is ready."
    )


def run_project(requirement):

    # ---------------------------------------------------------
    # STEP 0 — Prepare clean workspace
    # ---------------------------------------------------------

    prepare_workspace()

    state = ProjectState(
        user_requirement=requirement
    )

    # ---------------------------------------------------------
    # STEP 1 — Project Manager
    # ---------------------------------------------------------

    print(
        "\nRunning Project Manager..."
    )

    requirements = analyze_requirement(
        state.user_requirement
    )

    state.project_requirements = requirements

    print(
        "Project Manager completed."
    )

    # ---------------------------------------------------------
    # STEP 2 — Architect
    # ---------------------------------------------------------

    print(
        "\nRunning Architect..."
    )

    design = design_project(
        state.project_requirements,
        state.user_requirement
    )

    state.technical_design = design

    print(
        "Architect completed."
    )

    # ---------------------------------------------------------
    # STEP 3 — Coding Agent
    # ---------------------------------------------------------

    print(
        "\nRunning Coding Agent..."
    )

    code = generate_code(
        state.user_requirement,
        state.project_requirements,
        state.technical_design
    )

    python_files = [
        filename
        for filename in
        state.technical_design.folder_structure
        if filename.endswith(".py")
    ]

    if not python_files:

        raise ValueError(
            "Architect did not provide a Python source file."
        )

    source_filename = python_files[0]

    print(
        f"Coding Agent: saving generated code "
        f"to {source_filename}"
    )

    create_file(
        source_filename,
        code
    )

    print(
        "Coding Agent completed."
    )

    # ---------------------------------------------------------
    # STEP 4 — Testing Agent
    # ---------------------------------------------------------

    print(
        "\nRunning Testing Agent..."
    )

    test_result = run_testing_agent(
        state.user_requirement
    )

    state.test_result = test_result

    print(
        "Testing Agent completed."
    )

    # ---------------------------------------------------------
    # STEP 5 — Debugging Loop
    # ---------------------------------------------------------

    while not state.test_result.passed:

        if state.iteration >= MAX_DEBUG_ITERATIONS:

            print(
                "\nMaximum debugging iterations reached."
            )

            break

        state.iteration += 1

        print(
            f"\n========== DEBUGGING ITERATION "
            f"{state.iteration} / "
            f"{MAX_DEBUG_ITERATIONS} =========="
        )

        # -----------------------------------------------------
        # Debugger
        # -----------------------------------------------------

        print(
            "\nRunning Debugger..."
        )

        debug_result = run_debugger(
            state.user_requirement,
            state.test_result
        )

        state.debug_result = debug_result

        state.debugging_history.append(
            debug_result
        )

        print(
            "Debugger completed."
        )

        # -----------------------------------------------------
        # Run the SAME existing test suite again
        # -----------------------------------------------------

        print(
            "\nRunning existing tests again..."
        )

        test_result = run_tests()

        state.test_result = test_result

        print(
            "Existing tests completed."
        )

        if state.test_result.passed:

            print(
                "\nTests PASSED after debugging! ✅"
            )

        else:

            print(
                "\nTests still FAILED. ❌"
            )

    return state


if __name__ == "__main__":

    requirement = """
    Create a simple Python calculator program
    with functions for addition and subtraction.
    """

    final_state = run_project(
        requirement
    )

    print(
        "\n=============================="
    )

    print(
        "FINAL PROJECT STATE"
    )

    print(
        "=============================="
    )

    print(
        f"Iterations: {final_state.iteration}"
    )

    if final_state.test_result:

        print(
            f"Tests passed: "
            f"{final_state.test_result.passed}"
        )

        print(
            f"Exit code: "
            f"{final_state.test_result.exit_code}"
        )

    print(
        "=============================="
    )