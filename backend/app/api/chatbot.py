# backend/app/api/chatbot.py
import logging
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services import ollama_service

router = APIRouter()

# --- Request model ---
class ChatRequest(BaseModel):
    question: str
    model_name: str = "granite4:tiny-h"
    max_tokens: int = 512

# --- Define the context about your application ---
# This text will be given to the LLM so it knows about the app.
APP_CONTEXT = """
This is an LLM Platform application with the following features:
- Authentication: Users can register and log in.
- Model Hub: Users can select a base LLM (like llama3, mistral, gemma, codellama) and an optional LoRA adapter. They can then chat with the selected combination. Models with adapters are loaded dynamically.
- Train Custom Model: Users can upload a file (PDF, DOCX, XLSX) to simulate training a LoRA adapter based on its content. A placeholder adapter file is generated.
- SQL Trainer: Users can provide a database schema (JSON format) to generate synthetic SQL question/query pairs. They can then simulate training a SQL-focused LoRA adapter using this data. A placeholder adapter file is generated.
- File Analysis: Users can upload an Excel file (.xlsx, .xls), view a data preview, select columns, and generate basic charts (bar, line, scatter).
- Image OCR: Users can upload an image (PNG, JPG) to extract text using a multimodal model (LLaVA).
- Settings: Users can manage LoRA adapters (upload/download placeholder files) and placeholder profile/theme settings.

The application uses FastAPI (Python) for the backend and React (JavaScript) for the frontend. Ollama runs locally to serve the models. LoRA training is currently simulated by creating placeholder files.
"""
# --- Chat endpoint ---
@router.post("/ask")
async def ask_chatbot(request: ChatRequest):
    """
    Streams responses from the model for a given user question.
    """
    try:
        # ✅ Call Ollama service
        stream = ollama_service.run_prompt(
            model_name=request.model_name,
            prompt_text=request.question,  # fixed: use question, not request.request
            max_tokens=request.max_tokens,
        )

        # ✅ Stream the responses back to client
        async def response_generator():
            async for chunk in stream:
                if isinstance(chunk, dict) and "response" in chunk:
                    yield json.dumps({"response": chunk["response"]}) + "\n"

        return StreamingResponse(response_generator(), media_type="application/x-ndjson")

    except Exception as e:
        logging.error(f"Error during chatbot stream generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during chatbot stream generation: {e}")