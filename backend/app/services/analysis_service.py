# backend/app/api/analysis.py
from fastapi import APIRouter, UploadFile, File, Depends
from typing import Any, Dict
import pandas as pd
import io
from app.api.auth import require_auth_user

router = APIRouter()

@router.post("/upload-csv")
async def analyze_csv(file: UploadFile = File(...), user=Depends(require_auth_user)) -> Dict[str, Any]:
    """
    Protected. User uploads CSV, we do a tiny summary.
    """
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    preview = df.head(5).to_dict(orient="records")
    summary = {
        "rows": len(df),
        "cols": list(df.columns),
    }
    return {
        "preview_rows": preview,
        "summary": summary,
    }
