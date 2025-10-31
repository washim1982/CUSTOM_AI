# backend/app/api/chat_history.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.api.auth import require_auth_user

router = APIRouter()

# In-memory store for now
_CHAT_STORE: Dict[str, List[Dict[str, str]]] = {}

class ChatMessage(BaseModel):
    sender: str   # "user" | "model"
    text: str

class ChatConversation(BaseModel):
    id: str
    title: str
    messages: List[ChatMessage]

@router.get("/", response_model=List[ChatConversation])
async def list_chats(user=Depends(require_auth_user)):
    """
    Protected. Return all chats for this user.
    """
    uid = user.get("sub")
    return _CHAT_STORE.get(uid, [])


@router.post("/", response_model=ChatConversation)
async def save_chat(conv: ChatConversation, user=Depends(require_auth_user)):
    """
    Protected. Save or upsert a chat convo for this user.
    """
    uid = user.get("sub")
    if not uid:
        raise HTTPException(status_code=400, detail="Missing user subject in token")

    user_chats = _CHAT_STORE.setdefault(uid, [])
    # upsert by id
    for idx, existing in enumerate(user_chats):
        if existing["id"] == conv.id:
            user_chats[idx] = conv.dict()
            break
    else:
        user_chats.append(conv.dict())

    return conv
