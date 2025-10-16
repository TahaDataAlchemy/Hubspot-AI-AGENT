from datetime import datetime
from typing import List ,Optional,Dict,Any
from pydantic import BaseModel,Field
import uuid

class ToolCall(BaseModel):
    tool_call_id:str
    function_name:str
    arguments:Dict[str,Any]
    response:Dict[str,Any]
    execution_time_ms:Optional[int] = None
    status:str = "success"
    timestamp:datetime = Field(default_factory=datetime.now)

class ReactCycle(BaseModel):
    cycle_number:int
    timestamp:Optional[str] = None
    tool_calls:List[ToolCall] = []
    tokens_used:Optional[int] = None

class Message(BaseModel):
    message_id:str = Field(default_factory=lambda:str(uuid.uuid4()))
    user_id:str
    #User query
    user_query:str
    user_query_timestamp:datetime = Field(default_factory=datetime.now)

    #AI Response
    ai_response:str
    ai_response_timestamp:datetime = Field(default_factory=datetime.now)

    # React agent cycles (full reasoning Chain)
    react_cycles:List[ReactCycle] = []

    #Metadate
    total_tokens:int = 0
    total_tool_calls: int = 0
    total_react_cycle:int = 0 
    response_time_Seconds:float = 0.0
    model:str = ""

    #status
    status:str = "completed"
    error:Optional[str] = None

    created_at : datetime =  Field(default_factory = datetime.now)
