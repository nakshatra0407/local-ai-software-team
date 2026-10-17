from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from orchestrator import run_project


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="AI Software Engineering Team API",
    description="REST API for the local AI Software Engineering Team",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================
# Allows the React frontend running on localhost:5173
# to communicate with this FastAPI backend.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# PROJECT STORAGE
# =========================================================

projects = {}


# =========================================================
# WORKSPACE
# =========================================================

WORKSPACE = Path("workspace").resolve()


# =========================================================
# REQUEST MODELS
# =========================================================

class ProjectCreateRequest(BaseModel):
    requirement: str


# =========================================================
# RESPONSE MODELS
# =========================================================

class ProjectCreateResponse(BaseModel):
    project_id: str
    message: str
    requirement: str


class ProjectRunResponse(BaseModel):
    project_id: str
    status: str
    tests_passed: bool
    iterations: int


class DebugAttempt(BaseModel):
    file_modified: str
    explanation: str
    error_analysis: str


class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    tests_passed: bool | None
    iterations: int
    debugging_attempts: list[DebugAttempt]


class ProjectFile(BaseModel):
    filename: str
    content: str


class ProjectFilesResponse(BaseModel):
    project_id: str
    files: list[ProjectFile]


class ProjectTestsResponse(BaseModel):
    project_id: str
    tests_passed: bool | None
    exit_code: int | None
    stdout: str
    stderr: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "AI Software Engineering Team API is running"
    }


# =========================================================
# CREATE PROJECT
# =========================================================

@app.post(
    "/projects",
    response_model=ProjectCreateResponse
)
def create_project(request: ProjectCreateRequest):

    if not request.requirement.strip():
        raise HTTPException(
            status_code=400,
            detail="Project requirement cannot be empty."
        )

    project_id = str(uuid.uuid4())

    projects[project_id] = {
        "requirement": request.requirement,
        "status": "created",
        "state": None
    }

    return ProjectCreateResponse(
        project_id=project_id,
        message="Project created successfully",
        requirement=request.requirement
    )


# =========================================================
# RUN PROJECT
# =========================================================

@app.post(
    "/projects/{project_id}/run",
    response_model=ProjectRunResponse
)
def run_project_api(project_id: str):

    if project_id not in projects:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    project = projects[project_id]

    project["status"] = "running"

    try:

        # Call the EXISTING AI Software Engineering Team.
        state = run_project(
            project["requirement"]
        )

        project["state"] = state
        project["status"] = "completed"

        tests_passed = False

        if state.test_result is not None:
            tests_passed = state.test_result.passed

        return ProjectRunResponse(
            project_id=project_id,
            status="completed",
            tests_passed=tests_passed,
            iterations=state.iteration
        )

    except Exception as error:

        project["status"] = "failed"

        raise HTTPException(
            status_code=500,
            detail=f"Project execution failed: {error}"
        )


# =========================================================
# PROJECT STATUS
# =========================================================

@app.get(
    "/projects/{project_id}/status",
    response_model=ProjectStatusResponse
)
def get_project_status(project_id: str):

    if project_id not in projects:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    project = projects[project_id]

    tests_passed = None
    iterations = 0
    debugging_attempts = []

    if project["state"] is not None:

        state = project["state"]

        iterations = state.iteration

        if state.test_result is not None:
            tests_passed = state.test_result.passed

        debugging_attempts = [
            DebugAttempt(
                file_modified=attempt.file_modified,
                explanation=attempt.explanation,
                error_analysis=attempt.error_analysis
            )
            for attempt in state.debugging_history
        ]

    return ProjectStatusResponse(
        project_id=project_id,
        status=project["status"],
        tests_passed=tests_passed,
        iterations=iterations,
        debugging_attempts=debugging_attempts
    )


# =========================================================
# PROJECT FILES
# =========================================================

@app.get(
    "/projects/{project_id}/files",
    response_model=ProjectFilesResponse
)
def get_project_files(project_id: str):

    if project_id not in projects:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    if not WORKSPACE.is_dir():
        raise HTTPException(
            status_code=404,
            detail="Project workspace not found."
        )

    files = []

    for file_path in WORKSPACE.iterdir():

        if not file_path.is_file():
            continue

        # Never expose pytest cache or other hidden
        # development files through this API.
        if file_path.name.startswith("."):
            continue

        try:
            content = file_path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:
            content = "[Binary or non-text file]"

        files.append(
            ProjectFile(
                filename=file_path.name,
                content=content
            )
        )

    return ProjectFilesResponse(
        project_id=project_id,
        files=files
    )


# =========================================================
# PROJECT TESTS
# =========================================================

@app.get(
    "/projects/{project_id}/tests",
    response_model=ProjectTestsResponse
)
def get_project_tests(project_id: str):

    if project_id not in projects:
        raise HTTPException(
            status_code=404,
            detail="Project not found."
        )

    project = projects[project_id]

    if project["state"] is None:

        return ProjectTestsResponse(
            project_id=project_id,
            tests_passed=None,
            exit_code=None,
            stdout="",
            stderr=""
        )

    state = project["state"]

    if state.test_result is None:

        return ProjectTestsResponse(
            project_id=project_id,
            tests_passed=None,
            exit_code=None,
            stdout="",
            stderr=""
        )

    test_result = state.test_result

    return ProjectTestsResponse(
        project_id=project_id,
        tests_passed=test_result.passed,
        exit_code=test_result.exit_code,
        stdout=test_result.stdout,
        stderr=test_result.stderr
    )