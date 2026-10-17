from urllib import response

from qwen_client import ask_qwen
from models import ProjectRequirements
import json


SYSTEM_PROMPT = """
You are a Project Manager Agent.

Your job is to analyze a software requirement and create a project plan.

Return ONLY valid JSON.

The JSON MUST have exactly this structure:

{
    "functional_requirements": [
        "requirement 1",
        "requirement 2"
    ],
    "non_functional_requirements": [
        "requirement 1",
        "requirement 2"
    ],
    "tasks": [
        "task 1",
        "task 2"
    ]
}

Rules:

1. functional_requirements MUST be a list of strings.
2. non_functional_requirements MUST be a list of strings.
3. tasks MUST be a list of strings.
4. Do NOT put dictionaries or objects inside these lists.
5. Identify what the software must do as functional requirements.
6. Identify qualities or constraints as non-functional requirements.
7. Break the project into practical implementation tasks.
8. Do not write source code.
9. Do not add explanations outside the JSON.
10. If there are no clear non-functional requirements, return an empty list.
"""


def analyze_requirement(requirement):

    prompt = f"""
{SYSTEM_PROMPT}

USER REQUIREMENT:
{requirement}

Return the structured JSON now.
"""

    response = ask_qwen(prompt)
    print("\n===== RAW PROJECT MANAGER RESPONSE =====")
    print(response)
    print("===== END RAW RESPONSE =====\n")

    try:
        result = json.loads(response)
        validated_result = ProjectRequirements.model_validate(result)
    except json.JSONDecodeError:
        raise ValueError("Project Manager returned invalid JSON.")

    return validated_result


if __name__ == "__main__":

    requirement = """
    Create a simple task management application where
    users can create tasks, view tasks, update tasks,
    and delete tasks.
    """

    result = analyze_requirement(requirement)

    print("PROJECT MANAGER OUTPUT:")
    print(json.dumps(result.model_dump(), indent=4))