# backend/app/api/loras.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import os
import shutil
from typing import List
from app.api.auth import require_auth_user

router = APIRouter()

LORA_DIR = "/code/loras"
os.makedirs(LORA_DIR, exist_ok=True)

@router.get("/", response_model=List[str])
async def list_loras(user=Depends(require_auth_user)):
    """
    Protected. List LoRA adapter files we've uploaded.
    """
    files = []
    for name in os.listdir(LORA_DIR):
        full = os.path.join(LORA_DIR, name)
        if os.path.isfile(full):
            files.append(name)
    return files


@router.post("/upload")
async def upload_lora(file: UploadFile = File(...), user=Depends(require_auth_user)):
    """
    Protected. Upload LoRA adapter.
    """
    target_path = os.path.join(LORA_DIR, file.filename)
    with open(target_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    return {"status": "ok", "filename": file.filename}
