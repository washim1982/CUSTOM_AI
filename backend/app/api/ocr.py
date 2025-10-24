# backend/app/api/ocr.py
import ollama
import base64
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
import logging
from app.core.file_validation import validate_upload_file, ALLOWED_IMAGE_TYPES # Import validator
router = APIRouter()
logging.basicConfig(level=logging.INFO)

# Define the multimodal model to use for OCR
OCR_MODEL = "llava:latest" # Or another multimodal model you downloaded

class OcrResponse(BaseModel):
    extracted_text: str

@router.post("/process-image", response_model=OcrResponse)
async def process_image_for_ocr(
    file: UploadFile = File(...)
):
    """
    Accepts an image file, sends it to a multimodal model,
    and returns the extracted text.
    """
    # --- VALIDATE AND GET CONTENT ---
    contents = await validate_upload_file(file, allowed_types=ALLOWED_IMAGE_TYPES)
    # --- END VALIDATION ---
    try:
        logging.info(f"Received file '{file.filename}' for OCR.")
        #contents = await file.read()
        contents_bytes = await validate_upload_file(file, allowed_types=ALLOWED_IMAGE_TYPES)
        # Encode the image bytes as base64
        image_base64 = base64.b64encode(contents_bytes).decode('utf-8')
        logging.info(f"Image encoded to base64 (first 100 chars): {image_base64[:100]}...")
        # --- END OF FIX ---

        # Prepare the request for Ollama's multimodal model
        response = ollama.generate(
            model=OCR_MODEL,
            # Prompt specifically asking for OCR
            prompt="Extract all text from this image.",
            images=[image_base64], # Pass the base64 encoded image
            stream=False # Get the full response at once for simplicity here
        )
        logging.info(f"Ollama response received.")

        extracted_text = response.get('response', '').strip()
        logging.info(f"Extracted text (first 100 chars): {extracted_text[:100]}...")

        return {"extracted_text": extracted_text}

    except ollama.ResponseError as e:
        logging.error(f"Ollama API error during OCR: {e.error}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ollama API error: {e.error}")
    except Exception as e:
        logging.error(f"Failed to process image for OCR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")
    finally:
        await file.close()