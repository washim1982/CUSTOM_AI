# backend/app/main.py
import logging
import asyncio
import os
import requests
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.api import (
    auth,
    models as api_models,
    training,
    loras,
    analysis,
    ocr,
    chatbot,
    chat_history
)
from app.core.database import engine, Base
from app.services import ollama_service

# ---------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# FastAPI app initialization
# ---------------------------------------------------------------------
app = FastAPI(title="Imaginarium AI")
app.include_router(chat_history.router)

if os.getenv("FORCE_HTTPS", "false").lower() == "true":
    app.add_middleware(HTTPSRedirectMiddleware)

# ---------------------------------------------------------------------
# CORS (Frontend communication)
# ---------------------------------------------------------------------
origins = [
    "https://custom-data.xenomorphy-ai.com",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------------------
# Helper: Wait for Ollama API before startup
# ---------------------------------------------------------------------
async def wait_for_ollama(max_retries=20, delay=5):
    """Wait until Ollama API is reachable."""
    base_host = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
    # ✅ Always target the correct endpoint
    url = f"{base_host}/api/tags"
    logger.info(f"🔄 Waiting for Ollama to be available at {url} ...")

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.ok:
                logger.info(f"✅ Ollama is reachable (attempt {attempt})")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama not ready yet (attempt {attempt}/{max_retries}): {e}")
        await asyncio.sleep(delay)

    logger.error("❌ Ollama service did not respond in time.")
    return False

# ---------------------------------------------------------------------
# Startup event (model preload)
# ---------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Wait for Ollama, then preload the default model."""
    model_to_load = "granite4:tiny-h"
    logger.info(f"--- Application Startup: Preparing to preload model: {model_to_load} ---")

    available = await wait_for_ollama()
    if not available:
        logger.error("⚠️ Ollama API unavailable. Skipping model preload.")
        return

    try:
        asyncio.create_task(
            ollama_service.set_active_model(model_to_load, adapter_name=None)
        )
        logger.info(f"✅ Model preload task started for: {model_to_load}")
    except Exception as e:
        logger.error(f"--- FAILED to pre-load default model {model_to_load}: {e} ---")

# ---------------------------------------------------------------------
# Include API Routers
# ---------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(api_models.router, prefix="/api/models", tags=["Model Management"])
app.include_router(training.router, prefix="/api/training", tags=["Model Training"])
app.include_router(loras.router, prefix="/api/loras", tags=["LoRA Adapters"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Data Analysis"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])

# ---------------------------------------------------------------------
# Health + Root Endpoints
# ---------------------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "Welcome to the Imaginarium AI Platform API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
