# backend/app/api/ocr.py
import logging
import tempfile
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.services import ollama_service

router = APIRouter()

@router.post("/process-image")
async def process_image(
    file: UploadFile = File(...),
    mode: str = Query("describe", enum=["ocr", "describe"])
):
    """
    Process uploaded image for OCR or descriptive analysis.
    mode='ocr' → extract readable text.
    mode='describe' → provide contextual description and visible text.
    """
    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path = tmp.name

        logging.info(f"🖼️ Uploaded image saved to temp: {temp_path} (mode={mode})")

        # Call OCR logic with mode
        text = await ollama_service.run_ocr(temp_path, mode)

        return {"mode": mode, "extracted_text": text}

    except Exception as e:
        logging.error(f"❌ Failed to process image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process image: {e}")

    finally:
        file.file.close()
