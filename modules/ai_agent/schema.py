from pydantic import BaseModel
from typing import Dict, Optional

class AgentQueryRequest(BaseModel):
    query: str

