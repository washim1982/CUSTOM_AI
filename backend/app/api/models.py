# backend/app/api/models.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.api.auth import get_current_user, require_auth_user
from app.services import ollama_service

router = APIRouter()

# ------------------------------
# Schemas
# ------------------------------
class PromptRequest(BaseModel):
    prompt_text: str
    max_tokens: int = 256

# ------------------------------
# Routes
# ------------------------------

@router.get("/", response_model=List[Dict[str, Any]])
async def list_models():
    """
    Public. Returns local Ollama models for dropdowns etc.
    Also used by Training page to populate base model dropdown.
    """
    return ollama_service.list_local_models()


@router.post("/prompt")
async def run_prompt(req: PromptRequest, user=Depends(get_current_user)):
    """
    Chat endpoint for Model Hub:
    - anonymous  -> granite4 (Ollama)
    - logged in  -> MiniMax M2
    Returns {"text": "..."} single-shot response.
    """
    if not req.prompt_text.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    text = ollama_service.run_chat(
        prompt_text=req.prompt_text.strip(),
        max_tokens=req.max_tokens,
        user=user,
    )

    # 🔧 Fix duplicate word bug:
    # Some models sometimes echo like "Hello Hello" at the start.
    # We'll do a light dedupe of immediate word pairs at the beginning.
    # Only first ~20 tokens so we don't destroy legit repetition mid-sentence.
    import re
    tokens = text.split()
    cleaned_tokens = []
    i = 0
    while i < len(tokens):
        if i+1 < len(tokens) and tokens[i+1].lower() == tokens[i].lower():
            cleaned_tokens.append(tokens[i])
            i += 2
        else:
            cleaned_tokens.append(tokens[i])
            i += 1
        if len(cleaned_tokens) > 20:  # stop aggressive dedupe after 20 words
            cleaned_tokens.extend(tokens[i:])
            break
    cleaned = " ".join(cleaned_tokens)

    return {"text": cleaned}
