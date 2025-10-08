import json
import os
TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")

def get_tools():
    tools = []
    for file_name in os.listdir(TOOLS_DIR):
        if file_name.endswith(".json"):
            with open(os.path.join(TOOLS_DIR, file_name), "r", encoding="utf-8") as f:
                tools.append(json.load(f))
    return tools
