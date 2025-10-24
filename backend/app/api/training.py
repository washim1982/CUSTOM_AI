# backend/app/api/training.py
import json # <-- 1. Import the json library
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Body, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel # <-- Import BaseModel
from app.services import training_service
from app.core.file_validation import validate_upload_file, ALLOWED_TRAINING_TYPES # Import validator
router = APIRouter()

# --- Model for receiving JSON data ---

class SqlTrainingPayload(BaseModel):
    base_model: str
    custom_model_name: str
    qa_data: List[Dict[str, str]]

class TrainingDataPayload(BaseModel):
    base_model: str
    custom_model_name: str
    qa_data: List[Dict[str, str]]

@router.post("/generate-sql-data")
def generate_sql_data(
    schema_str: str = Form(..., alias="schema"), # <-- 2. Receive as string with alias
    num_examples: int = Form(50)
) -> List[Dict[str, str]]:
    """
    Generates synthetic SQL question-answer pairs from a database schema.
    The schema should be a JSON object mapping table names to a list of column names.
    """
    
    try:
        # --- 3. Parse the JSON string into a dictionary ---
        schema_dict = json.loads(schema_str)
        # ---------------------------------------------------
        if not isinstance(schema_dict, dict):
             raise ValueError("Schema must be a valid JSON object.")
        if not schema_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Schema cannot be empty."
            )
        qa_pairs = training_service.generate_sql_training_data(
            schema=schema_dict, # <-- 4. Pass the dictionary to the service 
            num_examples=num_examples
        )
        return qa_pairs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate training data: {e}",
        )

@router.post("/create-custom-model")
async def train_adapter_from_file( # Renamed endpoint function
    base_model: str = Form(...),
    custom_model_name: str = Form(...), # This will be the adapter name
    training_file: UploadFile = File(...)
):
    """Simulates training a LoRA adapter from an uploaded file."""
    # --- VALIDATE FILE ---
    # We don't need the content back here as the service only uses the filename for placeholder
    # But validation ensures type/size are checked before proceeding.
    # To avoid reading the whole file just for validation if content isn't needed,
    # you could implement a lighter check (e.g., just headers if possible, or seek/tell).
    # For consistency, we use the full validator here.
    await validate_upload_file(training_file, allowed_types=ALLOWED_TRAINING_TYPES)
    # --- END VALIDATION ---
    try:
        result = training_service.train_lora_adapter_from_file( # Call renamed service function
            base_model=base_model,
            custom_model_name=custom_model_name,
            training_file=training_file
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-sql-model")
async def train_sql_adapter(payload: SqlTrainingPayload): # Renamed endpoint function
    """Simulates training a SQL LoRA adapter from generated QA data."""
    try:
        result = training_service.train_sql_lora_adapter( # Call renamed service function
            base_model=payload.base_model,
            custom_model_name=payload.custom_model_name,
            qa_data=payload.qa_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- MODIFIED: create_model endpoint ---
# @router.post("/create-custom-model")
# async def create_model(
#     request: Request, # Inject the Request object to check headers
#     base_model_form: Optional[str] = Form(None, alias="base_model"),
#     custom_model_name_form: Optional[str] = Form(None, alias="custom_model_name"),
#     training_file: Optional[UploadFile] = File(None)
# ):
#     """
#     Creates a new custom model in Ollama.
#     Checks Content-Type to determine how to parse the request.
#     """
#     content_type = request.headers.get("content-type")
#     base_model = None
#     custom_model_name = None
#     qa_data = None
#     file_upload = None # Use a different name for clarity

#     try:
#         # Case 1: JSON payload (from SQL Trainer)
#         if content_type and "application/json" in content_type:
#             try:
#                 json_body = await request.json()
#                 payload = TrainingDataPayload(**json_body) # Validate JSON
#                 base_model = payload.base_model
#                 custom_model_name = payload.custom_model_name
#                 qa_data = payload.qa_data
#             except (json.JSONDecodeError, ValidationError) as e:
#                  raise HTTPException(status_code=422, detail=f"Invalid JSON payload: {e}")

#         # Case 2: Form data (from generic Training page)
#         elif content_type and "multipart/form-data" in content_type:
#             # FastAPI automatically populates Form/File params for multipart
#             if base_model_form and custom_model_name_form and training_file:
#                  base_model = base_model_form
#                  custom_model_name = custom_model_name_form
#                  file_upload = training_file # Assign the file
#             else:
#                  raise HTTPException(
#                     status_code=400,
#                     detail="Missing required form fields (base_model, custom_model_name, training_file)."
#                  )
#         # Case 3: Unsupported Content Type
#         else:
#              raise HTTPException(
#                 status_code=415,
#                 detail=f"Unsupported Content-Type: {content_type}. Use application/json or multipart/form-data."
#             )

#         # --- Call the service function ---
#         result = training_service.create_custom_model_from_data(
#             base_model=base_model,
#             custom_model_name=custom_model_name,
#             training_file=file_upload, # Pass the file or None
#             qa_data=qa_data          # Pass the data or None
#         )
#         return result

#     except HTTPException as http_exc:
#         raise http_exc # Re-raise known HTTP errors
#     except Exception as e:
#         # Catch unexpected errors during service call
#         raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")