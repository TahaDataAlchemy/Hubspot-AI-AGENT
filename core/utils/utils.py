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