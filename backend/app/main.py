import logging
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import os

from app.api import (
    auth,
    models as api_models,
    training,
    loras,
    analysis,
    ocr,
    chatbot,
    chat_history,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Imaginarium AI")

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "https://custom-data.xenomorphy-ai.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(api_models.router, prefix="/api/models", tags=["Model Hub"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(loras.router, prefix="/api/loras", tags=["LoRA"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])
app.include_router(chat_history.router, prefix="/api/chat-history", tags=["Chat History"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Imaginarium AI API"}

@app.get("/api/health")
def health():
    return {"status": "ok"}
