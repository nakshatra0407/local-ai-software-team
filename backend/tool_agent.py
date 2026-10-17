from qwen_client import ask_qwen
from tools import TOOLS, TOOL_DESCRIPTIONS


def build_tool_prompt(user_request):
    tool_information = ""

    for name, details in TOOL_DESCRIPTIONS.items():
        tool_information += (
            f"Tool: {name}\n"
            f"Description: {details['description']}\n"
            f"Parameters: {details['parameters']}\n\n"
        )

    prompt = f"""
You are an AI Coding Agent.

You have access to these tools:

{tool_information}

User request:
{user_request}

Choose the appropriate tool.

Respond in exactly ONE of these formats:

TOOL: list_files

TOOL: read_file | filename

TOOL: create_file | filename | content

TOOL: edit_file | filename | content

Do not add explanations.
"""

    return prompt


def run_agent(user_request):
    prompt = build_tool_prompt(user_request)

    response = ask_qwen(prompt).strip()

    print("Qwen requested:")
    print(response)

    if response == "TOOL: list_files":
        return TOOLS["list_files"]()

    if response.startswith("TOOL: read_file"):
        parts = response.split("|", 1)
        filename = parts[1].strip()

        return TOOLS["read_file"](filename)

    if response.startswith("TOOL: create_file"):
        parts = response.split("|", 2)
        filename = parts[1].strip()
        content = parts[2].strip()

        return TOOLS["create_file"](filename, content)

    if response.startswith("TOOL: edit_file") or response.startswith("TOOLS: edit_file"):
        parts = response.split("|", 2)
        filename = parts[1].strip()
        content = parts[2].strip()

        return TOOLS["edit_file"](filename, content)

    return response


if __name__ == "__main__":

    print("\n--- READ FILE ---")

    result = run_agent(
        "Read the contents of hello.py."
    )

    print("\nAgent result:")
    print(result)


    print("\n--- CREATE FILE ---")

    result = run_agent(
        'Create a file called copy_agent.py containing print("Created by agent")'
    )

    print("\nAgent result:")
    print(result)


    print("\n--- EDIT FILE ---")

    result = run_agent(
         'Edit test_agent.py so it contains print("Updated by agent")'
)

    print("\nAgent result:")
    print(result)