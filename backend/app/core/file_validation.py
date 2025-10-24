# backend/app/core/file_validation.py

from fastapi import HTTPException, UploadFile, status
import shutil
import os
from typing import List, Optional

# --- Configuration ---
MAX_FILE_SIZE_MB = 100 # Set max file size in Megabytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Define allowed MIME types or extensions per endpoint type
ALLOWED_TRAINING_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # .docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # .xlsx
    "application/vnd.ms-excel", # .xls
    "text/plain", # .txt
    "application/json", # .json
}
ALLOWED_EXCEL_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", # .xlsx
    "application/vnd.ms-excel", # .xls
}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_LORA_TYPES = { # Common adapter file types
    "application/octet-stream", # Often used for .bin or .safetensors
    # Add specific MIME types if known, otherwise rely on extension
}
ALLOWED_LORA_EXTENSIONS = {".safetensors", ".bin", ".pt"} # Check filename extension

# --- Validation Function ---

async def validate_upload_file(
    file: UploadFile,
    allowed_types: Optional[set] = None,
    allowed_extensions: Optional[set] = None,
    max_size: int = MAX_FILE_SIZE_BYTES
):
    """
    Validates file type and size before fully processing.
    Reads the file content to check size accurately.
    Returns the file content as bytes.
    """
    # 1. Check File Type (MIME and/or Extension)
    file_type_ok = False
    if allowed_types and file.content_type in allowed_types:
        file_type_ok = True
    elif allowed_extensions and any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
         file_type_ok = True
    elif not allowed_types and not allowed_extensions: # No specific type check needed
        file_type_ok = True

    if not file_type_ok:
        allowed_str = ", ".join(list(allowed_types or []) + list(allowed_extensions or []))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: '{file.content_type}' or '{file.filename}'. Allowed: {allowed_str}",
        )

    # 2. Check File Size (Read content and check length)
    # Read in chunks to avoid loading huge files entirely into memory if they exceed the limit early
    size = 0
    # Create a temporary file to store content while checking size
    # This avoids reading the whole thing into RAM if large
    temp_file = None
    try:
        # Use NamedTemporaryFile to get a file object compatible with shutil
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            size = temp_file.tell() # Get the size after writing

        if size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size ({size / (1024*1024):.2f} MB) exceeds limit ({MAX_FILE_SIZE_MB} MB).",
            )

        # If size is okay, read the content back from the temp file
        with open(temp_file.name, "rb") as f:
            content = f.read()
        return content

    except HTTPException as e:
         raise e # Re-raise HTTP exceptions directly
    except Exception as e:
        # Catch potential file reading errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not read or process file: {e}"
        )
    finally:
        # Ensure temp file is cleaned up
        if temp_file and os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        await file.close() # Close the original UploadFile stream

# Need to import tempfile for the above function
import tempfile