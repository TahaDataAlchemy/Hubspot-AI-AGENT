import os
import re
import json
import time
from datetime import datetime
def jsonload(token_file: str):
    with open(token_file, "r") as f:
        return json.load(f)

# ---------- Utility: Dump token (refresh flow) ----------
def jsonDumpRefreshToken(token_file: str, new_token_data: dict):
    with open(token_file, "w") as f:
        json.dump(new_token_data, f)

# ---------- Utility: Dump token (standard flow) ----------
def jsonDump(token_file: str, token_data: dict):
    with open(token_file, "w") as f:
        json.dump(token_data, f)

def message_to_dict(msg):
    """Convert ChatCompletionMessage or dict to plain dict"""
    if isinstance(msg, dict):
        return msg
    
    # Convert Groq ChatCompletionMessage to dict
    msg_dict = {
        "role": msg.role,
        "content": msg.content
    }
    
    # Add tool_calls if present
    if hasattr(msg, 'tool_calls') and msg.tool_calls:
        msg_dict["tool_calls"] = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in msg.tool_calls
        ]
    
    return msg_dict