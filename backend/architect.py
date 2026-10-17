from qwen_client import ask_qwen
from models import ProjectRequirements, TechnicalDesign
import json


SYSTEM_PROMPT = """
You are the Architect Agent in a local AI Software Engineering Team.

Your job is to design the architecture for the CURRENT software project.

IMPORTANT:
The CURRENT USER REQUIREMENT and the PROJECT MANAGER REQUIREMENTS
are the ONLY source of truth.

Never reuse architecture from a previous project.

Never assume the project is a calculator, to-do list, expense tracker,
API, or any other application unless the CURRENT USER REQUIREMENT
explicitly says so.

You must carefully derive the architecture from the requirements
provided in the current prompt.

Rules:

1. Design ONLY for the CURRENT project.

2. Follow every functional requirement from the Project Manager.

3. Do not invent unrelated functionality.

4. Do not reuse previous project filenames.

5. Do not reuse previous project components.

6. The folder structure must match the CURRENT project.

7. The components must describe functionality actually required
   by the CURRENT project.

8. Use Python unless the requirements explicitly require another
   technology.

9. Keep the architecture simple.

10. Do not add unnecessary databases, APIs, frameworks, or technologies.

11. This version of the system supports one Python source file.

12. Therefore folder_structure must contain exactly ONE .py file.

13. The components field should contain the main functions or
    functional parts required by the CURRENT user requirement.

14. Do not leave components empty when the project has clear
    functional requirements.

15. Return ONLY valid JSON.

16. Do not include Markdown.

17. Do not include explanations outside the JSON.

The JSON must have exactly this structure:

{
    "technology": ["Python"],
    "folder_structure": ["appropriate_current_project.py"],
    "components": ["component 1", "component 2"],
    "apis": [],
    "database": []
}
"""


def clean_json(response):
    response = response.strip()

    # Remove Markdown fences if Qwen adds them
    if response.startswith("```json"):
        response = response[len("```json"):].strip()

    elif response.startswith("```"):
        response = response[len("```"):].strip()

    if response.endswith("```"):
        response = response[:-3].strip()

    return response


def validate_design(
    design: TechnicalDesign,
    project_requirements: ProjectRequirements,
    user_requirement: str
):
    """
    Validate that the Architect designed the CURRENT project.
    """

    # ---------------------------------------------------------
    # 1. Exactly one Python source file
    # ---------------------------------------------------------

    python_files = [
        filename
        for filename in design.folder_structure
        if filename.endswith(".py")
    ]

    if len(python_files) != 1:
        raise ValueError(
            "Architect must provide exactly one Python source file."
        )

    # ---------------------------------------------------------
    # 2. Detect previous-project contamination
    # ---------------------------------------------------------

    combined_text = " ".join(
        design.folder_structure
        + design.components
        + design.apis
        + design.database
    ).lower()

    requirement_text = (
        user_requirement
        + " "
        + " ".join(
            project_requirements.functional_requirements
        )
        + " "
        + " ".join(
            project_requirements.tasks
        )
    ).lower()

    # Calculator-specific terms
    calculator_terms = [
        "calculator_app",
        "addition function",
        "subtraction function",
        "calculator",
        "addition",
        "subtraction"
    ]

    # Reject calculator architecture only when the
    # current requirement is NOT a calculator.
    if "calculator" not in requirement_text:

        for term in calculator_terms:

            if term in combined_text:
                raise ValueError(
                    "Architect generated previous-project "
                    f"calculator functionality: '{term}'."
                )

    # ---------------------------------------------------------
    # 3. Reject calculator filename
    # ---------------------------------------------------------

    filename = python_files[0].lower()

    if (
        filename == "calculator_app.py"
        and "calculator" not in requirement_text
    ):
        raise ValueError(
            "Architect generated calculator_app.py "
            "for a non-calculator project."
        )

    # ---------------------------------------------------------
    # 4. Components are NOT required for validation
    # ---------------------------------------------------------
    #
    # We intentionally do not reject an empty components list.
    #
    # The model may sometimes produce:
    #
    # "components": []
    #
    # That should not crash the entire project.
    #
    # The prompt still instructs Qwen to provide components.

    return design


def design_project(
    project_requirements: ProjectRequirements,
    user_requirement: str
):
    requirements_json = (
        project_requirements.model_dump_json(
            indent=2
        )
    )

    prompt = f"""
{SYSTEM_PROMPT}

==================================================
CURRENT USER REQUIREMENT
==================================================

{user_requirement}

==================================================
CURRENT PROJECT MANAGER REQUIREMENTS
==================================================

{requirements_json}

==================================================
ARCHITECTURE TASK
==================================================

Design the architecture for THIS CURRENT project.

First understand exactly what the user requested.

Then map every functional requirement to the architecture.

The filename and components MUST describe the CURRENT project.

For example, if the current requirement is:

"Create a Python program that manages a simple to-do list."

Then an appropriate architecture could contain:

"simple_to_do_list.py"

and components such as:

- add task
- remove task
- list tasks
- mark task as completed

It must NOT contain:

- calculator_app.py
- addition
- subtraction
- calculator functions

unless the CURRENT requirement explicitly asks for them.

Return ONLY JSON.
"""

    response = ask_qwen(prompt)

    print("\n===== RAW ARCHITECT RESPONSE =====")
    print(repr(response))
    print("===== END RAW RESPONSE =====")

    if not response.strip():
        raise ValueError(
            "Architect received an empty response."
        )

    cleaned_response = clean_json(response)

    try:
        data = json.loads(cleaned_response)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Architect returned invalid JSON: {error}"
        )

    try:
        design = TechnicalDesign(
            technology=data.get(
                "technology",
                ["Python"]
            ),
            folder_structure=data.get(
                "folder_structure",
                []
            ),
            components=data.get(
                "components",
                []
            ),
            apis=data.get(
                "apis",
                []
            ),
            database=data.get(
                "database",
                []
            )
        )

    except Exception as error:
        raise ValueError(
            f"Architect output failed validation: {error}"
        )

    # Validate the architecture
    validate_design(
        design,
        project_requirements,
        user_requirement
    )

    print("\nARCHITECT OUTPUT:")
    print(
        design.model_dump_json(
            indent=2
        )
    )

    return design


if __name__ == "__main__":

    requirements = ProjectRequirements(
        functional_requirements=[
            "Implement functionality for adding a task",
            "Implement functionality for deleting a task",
            "Implement functionality for listing all tasks",
            "Implement functionality for marking a task as completed"
        ],
        non_functional_requirements=[],
        tasks=[
            "Add functionality for adding a task",
            "Add functionality for removing a task",
            "Add functionality for listing all tasks",
            "Add functionality for marking a task as completed"
        ]
    )

    design = design_project(
        requirements,
        """
        Create a Python program that manages a simple to-do list.
        It should allow adding a task, removing a task,
        listing all tasks, and marking a task as completed.
        Store the tasks in memory using a Python list.
        """
    )

    print(design)