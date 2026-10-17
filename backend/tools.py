from pathlib import Path


WORKSPACE = Path("workspace").resolve()


def list_files():
    return [file.name for file in WORKSPACE.iterdir() if file.is_file()]


def read_file(filename):
    file_path = (WORKSPACE / filename).resolve()

    if WORKSPACE not in file_path.parents:
        raise ValueError("Access denied: file is outside the workspace.")

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    return file_path.read_text(encoding="utf-8")


def create_file(filename, content):
    file_path = (WORKSPACE / filename).resolve()

    if WORKSPACE not in file_path.parents:
        raise ValueError("Access denied: file is outside the workspace.")

    if file_path.exists():
        raise FileExistsError(f"File already exists: {filename}")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")

    return f"File created: {filename}"

def edit_file(filename, content):
    file_path = (WORKSPACE / filename).resolve()

    if WORKSPACE not in file_path.parents:
        raise ValueError("Access denied: file is outside the workspace.")

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")

    file_path.write_text(content, encoding="utf-8")

    return f"File updated: {filename}"
TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "create_file": create_file,
    "edit_file": edit_file
}


TOOL_DESCRIPTIONS = {
    "list_files": {
        "description": "List all files inside the controlled workspace.",
        "parameters": {}
    },
    "read_file": {
        "description": "Read the contents of a file inside the controlled workspace.",
        "parameters": {
            "filename": "string"
        }
    },
    "create_file": {
        "description": "Create a new file inside the controlled workspace.",
        "parameters": {
            "filename": "string",
            "content": "string"
        }
    },
    "edit_file": {
        "description": "Replace the contents of an existing file inside the controlled workspace.",
        "parameters": {
            "filename": "string",
            "content": "string"
        }
    }
}