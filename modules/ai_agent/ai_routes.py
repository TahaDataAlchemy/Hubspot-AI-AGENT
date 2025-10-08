from fastapi import APIRouter, HTTPException, Query
from modules.ai_agent.groq_client import run_convo
from core.logger.logger import LOG
from modules.ai_agent.schema import AgentQueryRequest
import asyncio

API_ROUTER = APIRouter(prefix="/api/v1/ai_agent", tags=["ai"])

@API_ROUTER.post("/chat")
async def chat_with_ai(prompt: AgentQueryRequest):
    try:
        LOG.info("User Querry Processing")
        response =run_convo(prompt)

        LOG.info(f"User query processed response: {response}")
        return {"response": response}
    except Exception as e:
        LOG.error(f"process Error: {str(e)}")
        raise HTTPException(status_code=500,detail=str(e))