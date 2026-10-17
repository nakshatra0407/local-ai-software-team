from state import ProjectState
from models import ProjectRequirements


state = ProjectState(
    user_requirement="Create a task management application."
)


state.project_requirements = ProjectRequirements(
    functional_requirements=[
        "Users can create tasks",
        "Users can view tasks",
        "Users can update tasks",
        "Users can delete tasks"
    ],
    non_functional_requirements=[
        "The application should be easy to use"
    ],
    tasks=[
        "Create task model",
        "Implement task API"
    ]
)


print("USER REQUIREMENT:")
print(state.user_requirement)

print("\nPROJECT REQUIREMENTS:")
print(state.project_requirements.model_dump())