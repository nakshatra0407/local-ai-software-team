from pydantic import BaseModel


class ProjectRequirements(BaseModel):
    functional_requirements: list[str]
    non_functional_requirements: list[str]
    tasks: list[str]


class TechnicalDesign(BaseModel):
    technology: list[str]
    folder_structure: list[str]
    components: list[str]
    apis: list[str]
    database: list[str]


class TestResult(BaseModel):
    passed: bool
    exit_code: int
    stdout: str
    stderr: str


class DebugResult(BaseModel):
    success: bool
    file_modified: str
    explanation: str
    error_analysis: str

class DebugPatch(BaseModel):
    file_to_modify: str
    old_code: str
    new_code: str
    explanation: str = "Debugger generated a targeted code patch."