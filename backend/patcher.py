from tools import read_file, edit_file
import ast


def get_python_definitions(code):
    """
    Return top-level Python function/class definitions.
    """

    try:

        tree = ast.parse(code)

    except SyntaxError as error:

        raise ValueError(
            f"Python syntax error: {error}"
        )

    definitions = set()

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef
            )
        ):

            definitions.add(
                node.name
            )

    return definitions


def validate_python_syntax(code):
    """
    Ensure Python code is syntactically valid.
    """

    try:

        ast.parse(code)

    except SyntaxError as error:

        raise ValueError(
            "Python syntax error: "
            f"{error}"
        )


def validate_patch_preserves_definitions(
    old_code,
    new_code
):
    """
    Ensure the patch itself does not remove
    functions/classes from the targeted code.
    """

    old_definitions = get_python_definitions(
        old_code
    )

    new_definitions = get_python_definitions(
        new_code
    )

    missing_definitions = (
        old_definitions
        - new_definitions
    )

    if missing_definitions:

        missing = ", ".join(
            sorted(
                missing_definitions
            )
        )

        raise ValueError(
            "Patch rejected because it removes "
            "existing functionality: "
            f"{missing}"
        )


def validate_complete_file(
    original_code,
    updated_code
):
    """
    Ensure the complete resulting file does not
    remove existing functions/classes.
    """

    original_definitions = get_python_definitions(
        original_code
    )

    updated_definitions = get_python_definitions(
        updated_code
    )

    missing_definitions = (
        original_definitions
        - updated_definitions
    )

    if missing_definitions:

        missing = ", ".join(
            sorted(
                missing_definitions
            )
        )

        raise ValueError(
            "Patch rejected because the resulting "
            "file removes existing functionality: "
            f"{missing}"
        )


def apply_patch(
    filename,
    old_code,
    new_code
):
    """
    Safely replace one exact code section.
    """

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    if not old_code.strip():

        raise ValueError(
            "old_code cannot be empty."
        )

    if not new_code.strip():

        raise ValueError(
            "new_code cannot be empty."
        )

    if old_code == new_code:

        raise ValueError(
            "old_code and new_code are identical."
        )

    # ---------------------------------------------------------
    # Read current file
    # ---------------------------------------------------------

    current_code = read_file(
        filename
    )

    # ---------------------------------------------------------
    # Ensure old_code exists exactly once
    # ---------------------------------------------------------

    occurrences = current_code.count(
        old_code
    )

    if occurrences == 0:

        raise ValueError(
            "The old_code was not found in the file."
        )

    if occurrences > 1:

        raise ValueError(
            "The old_code appears multiple times. "
            "Patch was rejected to avoid changing "
            "the wrong location."
        )

    # ---------------------------------------------------------
    # Validate replacement code itself
    # ---------------------------------------------------------

    validate_python_syntax(
        new_code
    )

    # ---------------------------------------------------------
    # Make sure the targeted patch does not remove
    # functions/classes.
    # ---------------------------------------------------------

    validate_patch_preserves_definitions(
        old_code,
        new_code
    )

    # ---------------------------------------------------------
    # Create the complete updated file
    # ---------------------------------------------------------

    updated_code = current_code.replace(
        old_code,
        new_code,
        1
    )

    # ---------------------------------------------------------
    # Validate COMPLETE resulting file
    # ---------------------------------------------------------

    validate_complete_file(
        current_code,
        updated_code
    )

    # ---------------------------------------------------------
    # Final syntax validation
    # ---------------------------------------------------------

    validate_python_syntax(
        updated_code
    )

    # ---------------------------------------------------------
    # Final AST parsing
    # ---------------------------------------------------------

    get_python_definitions(
        updated_code
    )

    # ---------------------------------------------------------
    # Write the file only after all validation passes.
    # ---------------------------------------------------------

    edit_file(
        filename,
        updated_code
    )

    return (
        f"Patch applied successfully to "
        f"{filename}."
    )