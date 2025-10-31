# backend/app/api/chatbot.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from app.api.auth import require_auth_user
from app.services import ollama_service

router = APIRouter()

class ChatbotRequest(BaseModel):
    message: str
    max_tokens: int = 256

@router.post("/message")
async def chatbot_message(req: ChatbotRequest, user=Depends(require_auth_user)) -> Dict[str, Any]:
    """
    Protected chatbot endpoint if you have a dedicated Chatbot tab.
    We'll just reuse run_minimax_prompt for logged-in users.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    text = ollama_service.run_minimax_prompt(req.message.strip(), req.max_tokens, user=user)

    return {"text": text}
