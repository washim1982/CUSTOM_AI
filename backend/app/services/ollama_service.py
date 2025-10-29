import inspect
import logging
import requests
import os
import tempfile
import json
from fastapi import HTTPException
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)

# ---- Ollama server endpoint ----
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

OLLAMA_LORA_DIR = "/loras"          # Shared mount inside Ollama container
BACKEND_LORA_DIR = "/code/loras"    # Same volume mount inside backend container

current_loaded_model: Optional[str] = None  # Track loaded model

# ----------------------------------------------------------------------
# HTTP Helper
# ----------------------------------------------------------------------
def _ollama_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """Wrapper for Ollama HTTP requests with basic error handling."""
    url = f"{OLLAMA_HOST}{endpoint}"
    try:
        r = requests.request(method, url, timeout=600, **kwargs)
        if not r.ok:
            logging.error(f"Ollama API error {r.status_code}: {r.text}")
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r
    except requests.RequestException as e:
        logging.error(f"❌ Ollama request to {url} failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama unreachable at {OLLAMA_HOST}")

# ----------------------------------------------------------------------
# OCR / Describe Image
# ----------------------------------------------------------------------
async def run_ocr(image_path: str, mode: str = "describe"):
    """
    Run OCR or generate descriptive text depending on the selected mode.
    """
    try:
        logging.info(f"Running OCR/Description mode={mode} on {image_path}")

        if mode == "ocr":
            prompt = (
                "Extract all readable text from this image exactly as it appears. "
                "Do not describe visuals — only text."
            )
        else:
            prompt = (
                "Describe this image in detail — include objects, layout, and visible text clearly."
            )

        payload = {
            "model": "llava:latest",
            "prompt": prompt,
            "images": [image_path],
        }
        response = _ollama_request("POST", "/generate", json=payload)
        data = response.json()
        text_output = data.get("response", str(data))
        result = text_output.strip()
        logging.info(f"✅ OCR/Describe completed ({len(result)} chars, mode={mode})")
        return result
    except Exception as e:
        logging.error(f"OCR/Description failed: {e}", exc_info=True)
        raise e

# ----------------------------------------------------------------------
# List Models
# ----------------------------------------------------------------------
def list_local_models() -> List[Dict[str, Any]]:
    """List all models available on the connected Ollama server."""
    try:
        url = f"{OLLAMA_HOST}/api/tags"
        logging.info(f"Requesting Ollama models from {url}")
        response = requests.get(url, timeout=10)
        logging.info(f"Ollama status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])
        logging.info(f"✅ Found {len(models)} models on Ollama host.")
        return [{"name": m.get("name")} for m in models if m.get("name")]

    except requests.exceptions.Timeout:
        logging.error("❌ Timeout contacting Ollama server.")
        raise HTTPException(status_code=504, detail="Ollama timeout")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"❌ Connection error: {e}")
        raise HTTPException(status_code=503, detail="Ollama connection failed")
    except Exception as e:
        logging.error(f"❌ list_local_models failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"list_local_models error: {e}")

# ----------------------------------------------------------------------
# Delete Model
# ----------------------------------------------------------------------
async def delete_ollama_model(model_name: str):
    """Delete a model from Ollama."""
    try:
        _ollama_request("DELETE", "/delete", json={"name": model_name})
        logging.info(f"🗑 Deleted model: {model_name}")
    except Exception as e:
        logging.warning(f"Could not delete model {model_name}: {e}")

# ----------------------------------------------------------------------
# Load Model
# ----------------------------------------------------------------------
async def set_active_model(base_model_name: str, adapter_name: Optional[str] = None):
    """Load or prepare model for generation."""
    global current_loaded_model
    new_model_to_load = base_model_name

    logging.info(f"Activating base model: {base_model_name}, adapter: {adapter_name}")
    if current_loaded_model == new_model_to_load:
        logging.info("✅ Model already active.")
        return {"status": "already_loaded", "loaded": current_loaded_model}

    try:
        _ollama_request("POST", "/generate", json={
            "model": new_model_to_load,
            "prompt": ".",
            "options": {"num_predict": 1},
            "keep_alive": "5m"
        })
        current_loaded_model = new_model_to_load
        logging.info(f"✅ Model {new_model_to_load} loaded successfully.")
        return {"status": "success", "loaded": current_loaded_model}
    except Exception as e:
        logging.error(f"Failed to load model {new_model_to_load}: {e}", exc_info=True)
        current_loaded_model = None
        raise HTTPException(status_code=500, detail=f"Failed to load model {new_model_to_load}")

# ----------------------------------------------------------------------
# Run Prompt
# ----------------------------------------------------------------------
async def run_prompt(model_name: str, prompt_text: str, max_tokens: int):
    """Stream responses from Ollama model via HTTP."""
    global current_loaded_model
    if not current_loaded_model or current_loaded_model != model_name:
        await set_active_model(model_name)

    url = f"{OLLAMA_HOST}/generate"
    payload = {
        "model": current_loaded_model,
        "prompt": prompt_text,
        "options": {"num_predict": max_tokens},
        "stream": True,
    }

    try:
        with requests.post(url, json=payload, stream=True) as r:
            for line in r.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        yield {"response": data["response"]}
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        logging.error(f"❌ Error running prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running prompt: {e}")
