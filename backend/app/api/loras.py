# backend/app/api/loras.py
import os
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from typing import List
from app.core.file_validation import validate_upload_file, ALLOWED_LORA_EXTENSIONS # Import validator
router = APIRouter()
LORA_DIR = "/code/loras" # Path inside the backend container

# Ensure LoRA directory exists
os.makedirs(LORA_DIR, exist_ok=True)

@router.get("/", response_model=List[str])
async def list_loras():
    """Lists available LoRA adapter files."""
    
    try:
        # List files, filter for common LoRA extensions
        files = [f for f in os.listdir(LORA_DIR)
                 if os.path.isfile(os.path.join(LORA_DIR, f)) and
                    (f.endswith(".safetensors") or f.endswith(".bin") or f.endswith(".pt"))]
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list LoRAs: {e}")

@router.post("/upload")
async def upload_lora(file: UploadFile = File(...)):
    """Uploads a LoRA adapter file."""
    
    file_path = os.path.join(LORA_DIR, file.filename)
    if os.path.exists(file_path):
         raise HTTPException(status_code=400, detail=f"File '{file.filename}' already exists.")

    try:
        # --- THIS IS THE FIX ---
        # 1. Validate and get the file content in bytes
        contents_bytes = await validate_upload_file(file, allowed_extensions=ALLOWED_LORA_EXTENSIONS)
        
        # 2. Write the bytes directly to the new file
        with open(file_path, "wb") as buffer:
            buffer.write(contents_bytes)
        # --- END OF FIX ---
            
        return {"filename": file.filename, "status": "uploaded"}
    
    except HTTPException as e:
        # Re-raise validation errors
        if os.path.exists(file_path):
            os.remove(file_path) # Clean up partial file
        raise e
    except Exception as e:
        # Clean up partial file if upload fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to upload LoRA: {e}")
    # No finally file.close() needed, validator handles it


@router.get("/download/{lora_name}")
async def download_lora(lora_name: str):
    """Downloads a specific LoRA adapter file."""
    file_path = os.path.join(LORA_DIR, lora_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail=f"LoRA '{lora_name}' not found.")
    return FileResponse(path=file_path, filename=lora_name, media_type='application/octet-stream')