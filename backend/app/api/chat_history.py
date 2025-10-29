# app/api/chat_history.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
#from app.auth import get_current_user
from typing import List
from pydantic import BaseModel
router = APIRouter(prefix="/api/chat-history", tags=["Chat History"])
chat_store = {}
class Chat(BaseModel):
    id: str
    title: str
    messages: list



@router.get("/")
def list_chats(user: str = "default_user"):
    return chat_store.get(user, [])

@router.post("/")
def save_chat(chat: Chat, user: str = "default_user"):
    if user not in chat_store:
        chat_store[user] = []
    existing = next((c for c in chat_store[user] if c["id"] == chat.id), None)
    if existing:
        existing.update(chat.dict())
    else:
        chat_store[user].append(chat.dict())
    return {"status": "ok"}

@router.get("/{chat_id}")
def get_chat(chat_id: str, user: str = "default_user"):
    return next((c for c in chat_store.get(user, []) if c["id"] == chat_id), {})

@router.delete("/{chat_id}")
def delete_chat(chat_id: str, user: str = "default_user"):
    if user in chat_store:
        chat_store[user] = [c for c in chat_store[user] if c["id"] != chat_id]
    return {"status": "deleted"}