from pydantic import BaseModel, Field

from models import (
    ProjectRequirements,
    TechnicalDesign,
    TestResult,
    DebugResult
)


class ProjectState(BaseModel):

    # Original requirement from the user
    user_requirement: str

    # Project Manager output
    project_requirements: ProjectRequirements | None = None

    # Architect output
    technical_design: TechnicalDesign | None = None

    # Latest Testing Agent result
    test_result: TestResult | None = None

    # Latest Debugger result
    debug_result: DebugResult | None = None

    # Current debugging iteration
    iteration: int = 0

    # History of all debugging attempts
    debugging_history: list[DebugResult] = Field(
        default_factory=list
    )