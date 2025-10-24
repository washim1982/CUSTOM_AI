# backend/app/api/chatbot.py
import ollama
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import json
from app.services import ollama_service # Import your existing service

router = APIRouter()
logging.basicConfig(level=logging.INFO)

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
# -------------------------------------------------

# Define the model to use for the chatbot
CHATBOT_MODEL = "mistral:latest" # Or llama3:8b, choose a good instruction-following model

class ChatRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_chatbot(request: ChatRequest) -> StreamingResponse:
    """
    Receives a question about the application and streams a response from the chatbot model.
    """
    try:
        # Construct the prompt for the LLM
        system_prompt = f"You are a helpful assistant knowledgeable about this specific web application. Use the following context to answer the user's question accurately. Context:\n{APP_CONTEXT}"
        
        # Format messages for Ollama chat (if using ollama.chat, otherwise adapt for ollama.generate)
        # Using ollama.generate for simplicity with existing service structure
        full_prompt = f"System: {system_prompt}\nUser: {request.question}\nAssistant:"

        logging.info(f"Sending prompt to {CHATBOT_MODEL} for chatbot request.")

        # Ensure the chatbot model is loaded (optional, depends on your ollama_service logic)
        # You might want a dedicated way to load/manage the chatbot model in ollama_service
        # For now, assume run_prompt handles loading if needed
        
        stream = await ollama_service.run_prompt(
            model_name=CHATBOT_MODEL,
            prompt_text=full_prompt,
            max_tokens=512 # Adjust as needed
        )

        async def response_generator():
            try:
                for chunk in stream:
                    # Send chunks as JSON for easier frontend parsing
                    yield json.dumps({"response": chunk.get('response', '')}) + "\n"
            except Exception as e:
                logging.error(f"Error during chatbot stream generation: {e}")
                yield json.dumps({"error": "An error occurred during streaming."}) + "\n"

        return StreamingResponse(response_generator(), media_type="application/x-ndjson")

    except Exception as e:
        logging.error(f"Chatbot request failed: {e}", exc_info=True)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to get response from chatbot: {str(e)}")