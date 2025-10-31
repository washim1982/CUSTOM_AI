# backend/app/api/training.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List
import os
import shutil
import logging

from app.api.auth import require_auth_user
from app.services import ollama_service

router = APIRouter()

UPLOAD_DIR = "/code/training_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/start")
async def start_training_adapter(
    base_model: str = Form(...),
    new_model_name: str = Form(...),
    training_file: UploadFile = File(...),
    user=Depends(require_auth_user),
):
    """
    Protected. User must be logged in.
    For now we just save the file and pretend we're kicking off LoRA training.
    """
    if not base_model:
        raise HTTPException(status_code=400, detail="base_model required")
    if not new_model_name:
        raise HTTPException(status_code=400, detail="new_model_name required")

    # save file
    file_path = os.path.join(UPLOAD_DIR, training_file.filename)
    with open(file_path, "wb") as out:
        shutil.copyfileobj(training_file.file, out)

    logging.info(
        f"[TRAINING] user={user.get('sub')} base={base_model} new={new_model_name} file={file_path}"
    )

    # TODO: launch real LoRA training pipeline
    return {
        "status": "started",
        "message": "Training kicked off (placeholder).",
        "base_model": base_model,
        "new_model_name": new_model_name,
        "data_file": training_file.filename,
    }


@router.get("/available-models", response_model=List[dict])
async def get_available_models(user=Depends(require_auth_user)):
    """
    Protected. Return list of base models you can fine-tune.
    Currently just our Ollama list.
    """
    return ollama_service.list_local_models()
