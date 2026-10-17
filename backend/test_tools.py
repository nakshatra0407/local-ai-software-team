from tools import TOOL_DESCRIPTIONS


print("Tool descriptions:")

for name, details in TOOL_DESCRIPTIONS.items():
    print(f"\nTool: {name}")
    print(f"Description: {details['description']}")
    print(f"Parameters: {details['parameters']}")