# backend/app/main.py

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api import auth, models as api_models, training, loras, analysis, ocr, chatbot
from app.core.database import engine, Base

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LLM Platform API")

# 2. Define the list of allowed origins (your frontend)
origins = ["http://localhost:3000"]


# Configure CORS (Cross-Origin Resource Sharing)
# This is important for allowing the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Adjust for your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers from different modules
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(api_models.router, prefix="/api/models", tags=["Model Management"])
app.include_router(training.router, prefix="/api/training", tags=["Model Training"])
app.include_router(loras.router, prefix="/api/loras", tags=["LoRA Adapters"]) # <-- Add LoRA router
app.include_router(analysis.router, prefix="/api/analysis", tags=["Data Analysis"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"]) # <-- Add OCR router
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"]) # <-- Add Chatbot router
@app.get("/")
def read_root():
    return {"message": "Welcome to the LLM Platform API"}
