# backend/app/api/ocr.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Dict, Any
import tempfile
import os
import logging
from app.api.auth import require_auth_user
from app.services import ollama_service

router = APIRouter()

@router.post("/")
async def run_ocr_endpoint(
    image: UploadFile = File(...),
    mode: str = "describe",
    user = Depends(require_auth_user)
) -> Dict[str, Any]:
    """
    Protected. OCR / Vision description endpoint.
    We call ollama_service.run_ocr(...) if you have it, else just placeholder.
    """
    try:
        # write the image to tmp and pass path to service
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await image.read())
            tmp_path = tmp.name

        # If you kept your old ollama_service.run_ocr() function, call it:
        if hasattr(ollama_service, "run_ocr"):
            result_text = ollama_service.run_ocr.__wrapped__(tmp_path, mode) \
                if hasattr(ollama_service.run_ocr, "__wrapped__") else \
                ollama_service.run_ocr(tmp_path, mode)
        else:
            result_text = "[OCR placeholder: Vision model not integrated]"

        os.unlink(tmp_path)
        return {"text": result_text}
    except Exception as e:
        logging.exception("OCR failed")
        raise HTTPException(status_code=500, detail=str(e))
