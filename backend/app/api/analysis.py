# backend/app/api/analysis.py
import io
import pandas as pd
import math # <-- 1. Import math
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from app.core.file_validation import validate_upload_file, ALLOWED_EXCEL_TYPES # Import validator
from app.services import analysis_service

router = APIRouter()

# Store uploaded file data temporarily (in-memory, replace with better storage if needed)
# A dictionary mapping a unique identifier (like user ID or session ID) to the DataFrame
uploaded_data_store: Dict[str, pd.DataFrame] = {}
# Simple session identifier for this example (replace with real user/session management)
CURRENT_SESSION_ID = "user1"


# --- Function to clean non-JSON compliant floats ---
def clean_non_json_floats(data):
    if isinstance(data, list):
        return [clean_non_json_floats(item) for item in data]
    elif isinstance(data, dict):
        return {k: clean_non_json_floats(v) for k, v in data.items()}
    elif isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return None # Replace NaN/inf/-inf with None (which becomes null in JSON)
    else:
        return data
# ---------------------------------------------------

@router.post("/upload-excel")
async def upload_excel_for_analysis(file: UploadFile = File(...)):
    """Uploads, validates, reads Excel, stores, returns preview."""
    # --- THIS IS THE FIX ---
    # 1. Validate the file. This reads it and returns the content as bytes.
    #    The original 'file' object is now closed.
    # file_content_bytes = await validate_upload_file(file, allowed_types=ALLOWED_EXCEL_TYPES)
    # --- END VALIDATION ---
    # if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
    #     raise HTTPException(status_code=400, detail="Invalid file type. Please upload an Excel file (.xlsx or .xls).")

    try:
        file_content_bytes = await validate_upload_file(
            file, 
            allowed_types=ALLOWED_EXCEL_TYPES, 
            allowed_extensions={".xlsx", ".xls"}
        )
        # Read the file content into an in-memory bytes buffer
        # contents = await file.read()
        excel_buffer = io.BytesIO(file_content_bytes)

        # Use the analysis service to read the data
        df = analysis_service.read_excel_to_dataframe(excel_buffer)

        # Store the DataFrame associated with the session ID
        uploaded_data_store[CURRENT_SESSION_ID] = df

        # Prepare preview data (e.g., first 5 rows)
        preview_data_raw = df.head().to_dict(orient='records')
        columns = df.columns.tolist()
        preview_data_cleaned = clean_non_json_floats(preview_data_raw)
        return {"columns": columns, "data": preview_data_cleaned}
    except HTTPException as e:
        # Re-raise validation errors
        raise e
    except Exception as e:
        # Catch errors from pandas or file processing
        raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {str(e)}")
    # No finally file.close() needed, validator handles it
    # --- END OF FIX ---

@router.post("/generate-chart")
async def generate_chart_from_data(
    x_axis_col: str = Form(...),
    y_axis_col: str = Form(...)
) -> StreamingResponse:
    """
    Generates a chart using the previously uploaded Excel data for the current session.
    """
    # Retrieve the stored DataFrame
    df = uploaded_data_store.get(CURRENT_SESSION_ID)
    if df is None:
        raise HTTPException(status_code=404, detail="No data uploaded for this session. Please upload an Excel file first.")

    if x_axis_col not in df.columns or y_axis_col not in df.columns:
         raise HTTPException(status_code=400, detail=f"Invalid column names: '{x_axis_col}' or '{y_axis_col}' not found.")

    try:
        # Use the analysis service to create the chart
        chart_buffer = analysis_service.create_chart_from_dataframe(
            df=df,
            x_axis_col=x_axis_col,
            y_axis_col=y_axis_col,
            chart_type='bar' # Or make this dynamic based on user selection
        )
        return StreamingResponse(chart_buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate chart: {str(e)}")