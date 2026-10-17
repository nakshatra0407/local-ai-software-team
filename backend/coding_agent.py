from pathlib import Path
import ast

from qwen_client import ask_qwen

from retriever import Retriever
from context_builder import build_context


# =========================================================
# RAG
# =========================================================

retriever = Retriever()


# =========================================================
# CONFIGURATION
# =========================================================

MAX_CODING_ATTEMPTS = 3


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are a Coding Agent in a local AI Software Engineering Team.

Your job is to generate the application code for the
CURRENT software requirement.

The CURRENT USER REQUIREMENT is the highest priority.

Rules:

1. Generate valid Python code.

2. Implement ONLY the current user requirement.

3. Carefully follow every functional requirement.

4. Carefully follow the Architect technical design.

5. If the Architect specifies functions or classes
   in the components field, IMPLEMENT them.

6. Do not omit required functions.

7. Do not rename required functions unless absolutely
   necessary.

8. Do not carry assumptions from previous projects.

9. Do not reuse functionality from previous projects
   unless the current requirement explicitly asks for it.

10. Do not reuse previous project names, filenames,
    functions, APIs, variables, or data structures
    unless they are appropriate for the CURRENT requirement.

11. Use the provided engineering knowledge only when
    relevant to the current requirement.

12. Keep the implementation simple and readable.

13. Do not add unnecessary technologies.

14. Do not add unnecessary features.

15. Do not create functionality that the user did not request.

16. Make the implementation easy to test.

17. The generated Python file will be imported by pytest.

18. NEVER execute application logic during module import.

19. Do not create example objects and immediately call
    their methods at the top level.

20. If demonstration code is useful, place it inside:

    if __name__ == "__main__":
        ...

21. Do not use interactive input() at module level.

22. Do not execute test scenarios at module level.

23. Return ONLY Python code.

24. Do not use Markdown code fences.

25. Do not include explanations before or after the code.

26. The generated application must be a fresh implementation
    for the CURRENT project.

27. Never assume the CURRENT project is a calculator,
    to-do list, expense tracker, API, or any other project
    unless the user explicitly requested it.

28. The original user requirement has higher priority than
    examples, retrieved knowledge, previous conversations,
    or previous generated projects.
"""


# =========================================================
# CODE CLEANING
# =========================================================

def clean_code(response):

    code = response.strip()

    if code.startswith("```python"):
        code = code[
            len("```python"):
        ].strip()

    elif code.startswith("```"):
        code = code[
            len("```"):
        ].strip()

    if code.endswith("```"):
        code = code[
            :-3
        ].strip()

    return code


# =========================================================
# PYTHON ANALYSIS
# =========================================================

def get_definitions(code):

    try:
        tree = ast.parse(code)

    except SyntaxError as error:

        raise ValueError(
            f"Generated code contains invalid Python syntax: {error}"
        )

    functions = set()
    classes = set()

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):
            functions.add(
                node.name
            )

        elif isinstance(
            node,
            ast.ClassDef
        ):
            classes.add(
                node.name
            )

    return functions, classes


# =========================================================
# ARCHITECT REQUIREMENT VALIDATION
# =========================================================

def validate_required_components(
    code,
    technical_design
):

    functions, classes = get_definitions(
        code
    )

    missing_components = []

    for component in technical_design.components:

        component_name = component.strip()

        # ---------------------------------------------
        # Function-like component
        # ---------------------------------------------

        if (
            component_name.isidentifier()
            and component_name not in functions
            and component_name not in classes
        ):
            missing_components.append(
                component_name
            )

    if missing_components:

        missing = ", ".join(
            missing_components
        )

        raise ValueError(
            "Coding Agent did not implement required "
            f"Architect components: {missing}"
        )

    return True


# =========================================================
# CURRENT PROJECT CONTAMINATION CHECK
# =========================================================

def validate_project_scope(
    code,
    requirement
):

    code_lower = code.lower()
    requirement_lower = requirement.lower()

    unrelated_terms = [
        "calculator_app",
        "addition function",
        "subtraction function",
        "expense_tracker",
        "password_generator",
        "weather_app"
    ]

    for term in unrelated_terms:

        if (
            term in code_lower
            and term not in requirement_lower
        ):

            raise ValueError(
                "Generated code contains unrelated "
                f"previous-project functionality: {term}"
            )


# =========================================================
# MODULE SAFETY
# =========================================================

def validate_module_safety(code):

    try:
        tree = ast.parse(code)

    except SyntaxError as error:

        raise ValueError(
            f"Invalid Python syntax: {error}"
        )

    for node in tree.body:

        # Ignore definitions/imports/constants.
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
                ast.Import,
                ast.ImportFrom,
                ast.Assign,
                ast.AnnAssign
            )
        ):
            continue

        # Ignore docstrings.
        if isinstance(
            node,
            ast.Expr
        ):

            if isinstance(
                node.value,
                ast.Constant
            ) and isinstance(
                node.value.value,
                str
            ):
                continue

        # Ignore the main guard.
        if isinstance(
            node,
            ast.If
        ):

            if (
                isinstance(
                    node.test,
                    ast.Compare
                )
            ):
                continue

        raise ValueError(
            "Generated application contains executable "
            "top-level logic. Application code should be "
            "safe to import."
        )


# =========================================================
# BUILD PROMPT
# =========================================================

def build_prompt(
    requirement,
    project_requirements,
    technical_design,
    rag_context,
    previous_error=None
):

    requirements_text = (
        project_requirements.model_dump_json(
            indent=2
        )
    )

    design_text = (
        technical_design.model_dump_json(
            indent=2
        )
    )

    retry_message = ""

    if previous_error:

        retry_message = f"""
==================================================
PREVIOUS GENERATION FAILED VALIDATION
==================================================

{previous_error}

You MUST correct this problem.

Do not repeat the same mistake.

==================================================
"""

    return f"""
{SYSTEM_PROMPT}

{retry_message}

==================================================
CURRENT USER REQUIREMENT
==================================================

{requirement}

==================================================
PROJECT MANAGER REQUIREMENTS
==================================================

{requirements_text}

==================================================
ARCHITECT TECHNICAL DESIGN
==================================================

{design_text}

==================================================
RETRIEVED ENGINEERING KNOWLEDGE
==================================================

{rag_context}

==================================================
IMPLEMENTATION REQUIREMENTS
==================================================

Implement EVERY required functional requirement.

The Architect components are especially important.

If the Architect says:

add_task
remove_task
list_tasks
mark_task_as_completed

then the generated Python file MUST actually define:

def add_task(...):
    ...

def remove_task(...):
    ...

def list_tasks(...):
    ...

def mark_task_as_completed(...):
    ...

Use appropriate arguments and implementation based on
the CURRENT USER REQUIREMENT.

Do not silently omit any required functionality.

==================================================
FINAL CHECK BEFORE RESPONSE
==================================================

Before returning the code, verify:

1. Is this the CURRENT project?
2. Does the code implement the user requirement?
3. Are all Architect components implemented?
4. Is the Python syntax valid?
5. Can pytest import the module safely?
6. Is there no calculator functionality unless requested?
7. Is there no previous-project contamination?
8. Is all demonstration code inside:

   if __name__ == "__main__":

Return ONLY Python source code.
"""


# =========================================================
# GENERATE CODE
# =========================================================

def generate_code(
    requirement,
    project_requirements,
    technical_design
):

    retrieved_chunks = retriever.retrieve(
        requirement
    )

    rag_context = build_context(
        retrieved_chunks
    )

    previous_error = None

    for attempt in range(
        1,
        MAX_CODING_ATTEMPTS + 1
    ):

        print(
            f"\nCoding Agent attempt "
            f"{attempt} / {MAX_CODING_ATTEMPTS}"
        )

        prompt = build_prompt(
            requirement,
            project_requirements,
            technical_design,
            rag_context,
            previous_error
        )

        response = ask_qwen(
            prompt
        )

        if not response.strip():

            previous_error = (
                "Coding Agent returned an empty response."
            )

            continue

        code = clean_code(
            response
        )

        if not code:

            previous_error = (
                "Coding Agent produced empty code."
            )

            continue

        try:

            # ---------------------------------------------
            # Syntax
            # ---------------------------------------------

            get_definitions(
                code
            )

            # ---------------------------------------------
            # Required components
            # ---------------------------------------------

            validate_required_components(
                code,
                technical_design
            )

            # ---------------------------------------------
            # Project contamination
            # ---------------------------------------------

            validate_project_scope(
                code,
                requirement
            )

            # ---------------------------------------------
            # Import safety
            # ---------------------------------------------

            validate_module_safety(
                code
            )

            print(
                "Coding Agent validation passed."
            )

            return code

        except Exception as error:

            print(
                f"Coding Agent attempt {attempt} "
                f"rejected:"
            )

            print(
                error
            )

            previous_error = str(
                error
            )

    raise RuntimeError(
        "Coding Agent failed to generate valid application "
        f"code after {MAX_CODING_ATTEMPTS} attempts. "
        f"Last error: {previous_error}"
    )


if __name__ == "__main__":

    print(
        "coding_agent.py should normally be called "
        "through the orchestrator."
    )