# backend/app/api/models.py
import logging 
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse # Import this
from typing import List, AsyncGenerator, Optional
from pydantic import BaseModel
import json
from fastapi import Depends
from app.core.auth0_middleware import auth0_guard
from app.services import ollama_service

router = APIRouter()

class ModelResponse(BaseModel):
    name: str

class LoadRequest(BaseModel):
    model_name: str
    adapter_name: Optional[str] = None
# --- THIS IS THE ENDPOINT THAT'S NOT BEING FOUND ---
@router.get("/", dependencies=[Depends(auth0_guard)])
def get_available_models():
    try:
        logging.info("GET /api/models called")
        models = ollama_service.list_local_models()
        logging.info(f"Models returned: {models}")
        return models
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama service: {e}")
# ----------------------------------------------------

@router.post("/load")
async def load_model_to_memory(request: LoadRequest):
    """
    Loads base model, optionally applying LoRA via temporary model.
    """
    try:
        return await ollama_service.set_active_model(request.model_name, request.adapter_name)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

class PromptRequest(BaseModel):
    model_name: str
    prompt_text: str
    max_tokens: int = 512

@router.post("/prompt/")
@router.post("/prompt")
async def run_model_prompt(request: PromptRequest) -> StreamingResponse:
    """
    Runs a prompt against a specified model.
    This endpoint will stream the response back to the client.
    """
    try:
        stream = ollama_service.run_prompt(
            model_name=request.model_name,
            prompt_text=request.prompt_text,
            max_tokens=request.max_tokens,
        )
        
        # We need a generator function to wrap the stream for StreamingResponse
        async def response_generator():
            async for chunk in stream:
                yield json.dumps({"response": chunk["response"]}) + "\n"
        return StreamingResponse(response_generator(), media_type="application/x-ndjson")
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500,
            detail=f"Error running prompt: {e}",
        )