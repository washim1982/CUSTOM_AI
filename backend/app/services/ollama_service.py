import ollama
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
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434").rstrip("/")
OLLAMA_LORA_DIR = "/loras"          # Shared mount inside Ollama container
BACKEND_LORA_DIR = "/code/loras"    # Same volume mount inside backend container

current_loaded_model: Optional[str] = None  # Track loaded model


# ----------------------------------------------------------------------
# Helper: Generic Ollama HTTP Request
# ----------------------------------------------------------------------
def _ollama_request(method: str, endpoint: str, **kwargs) -> requests.Response:
    """Wrapper for Ollama HTTP requests with error handling."""
    # ✅ Always ensure /api prefix
    if not endpoint.startswith("/api/"):
        endpoint = f"/api{endpoint if endpoint.startswith('/') else '/' + endpoint}"

    url = f"{OLLAMA_HOST}{endpoint}"
    logging.info(f"🌐 Request → {method.upper()} {url}")

    try:
        r = requests.request(method, url, timeout=600, **kwargs)
        if not r.ok:
            logging.error(f"❌ Ollama API error {r.status_code}: {r.text}")
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r
    except requests.RequestException as e:
        logging.error(f"❌ Ollama request to {url} failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ollama server unreachable at {OLLAMA_HOST}")


# ----------------------------------------------------------------------
# List Models
# ----------------------------------------------------------------------
def list_local_models() -> List[Dict[str, Any]]:
    """List all models available on the connected Ollama server."""
    try:
        url = f"{OLLAMA_HOST}/api/tags"
        logging.info(f"🔍 Requesting Ollama models from {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        models = data.get("models", [])
        logging.info(f"✅ Found {len(models)} models on Ollama host.")
        return [{"name": m.get("name")} for m in models if m.get("name")]

    except requests.exceptions.ConnectionError as e:
        logging.error(f"❌ Could not connect to Ollama service: {e}")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Ollama HTTP error: {e}")
        raise HTTPException(status_code=502, detail=f"Ollama HTTP error: {e}")
    except ValueError as e:
        logging.error(f"❌ Failed to parse Ollama response: {e}")
        raise HTTPException(status_code=500, detail="Invalid response from Ollama")
    except Exception as e:
        logging.error(f"❌ Unexpected error in list_local_models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ----------------------------------------------------------------------
# Delete Model
# ----------------------------------------------------------------------
async def delete_ollama_model(model_name: str):
    """Delete a model from Ollama (if temporary)."""
    try:
        _ollama_request("DELETE", "/api/delete", json={"name": model_name})
        logging.info(f"🗑️ Deleted model: {model_name}")
    except Exception as e:
        logging.warning(f"⚠️ Could not delete model {model_name}: {e}")


# ----------------------------------------------------------------------
# Create or Load Model
# ----------------------------------------------------------------------
async def set_active_model(base_model_name: str, adapter_name: Optional[str] = None):
    """Load a base model or create a temporary LoRA-combined model via Ollama HTTP API."""
    global current_loaded_model

    new_model_to_load = base_model_name
    temp_model_name = None
    apply_adapter = False
    if adapter_name in (None, "", "null", "string"):
        adapter_name = None
    logging.info(f"🧠 Activating model: {base_model_name}, adapter: {adapter_name}")
    logging.info(f"Currently loaded: {current_loaded_model}")

    # --- Validate adapter ---
    if adapter_name:
        adapter_path_backend = os.path.join(BACKEND_LORA_DIR, adapter_name)
        adapter_path_ollama = os.path.join(OLLAMA_LORA_DIR, adapter_name)

        if not os.path.exists(adapter_path_backend):
            raise HTTPException(status_code=404, detail=f"Adapter '{adapter_name}' not found.")
        size = os.path.getsize(adapter_path_backend)
        if size < 1 * 1024 * 1024:
            logging.warning(f"⚠️ Adapter '{adapter_name}' too small ({size} bytes) — likely placeholder, skipping.")
        else:
            apply_adapter = True

    # --- Apply adapter ---
    if apply_adapter:
        temp_model_name = f"{base_model_name}-with-{adapter_name.split('.')[0]}"
        new_model_to_load = temp_model_name

        if current_loaded_model == new_model_to_load:
            logging.info(f"Model {new_model_to_load} already active.")
            return {"status": "already_loaded", "loaded": new_model_to_load}

        modelfile_content = f"FROM {base_model_name}\nADAPTER {os.path.join(OLLAMA_LORA_DIR, adapter_name)}\n"
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".Modelfile") as tmp:
            tmp.write(modelfile_content)
            tmp_path = tmp.name
        try:
            logging.info(f"🧩 Creating temporary model '{temp_model_name}' via Ollama API...")
            with open(tmp_path, "r") as f:
                modelfile = f.read()
            _ollama_request("POST", "/api/create", json={"name": temp_model_name, "modelfile": modelfile})
            logging.info(f"✅ Created temporary model '{temp_model_name}' successfully.")
        except Exception as e:
            await delete_ollama_model(temp_model_name)
            raise HTTPException(status_code=500, detail=f"Failed to create temporary model: {e}")
        finally:
            os.remove(tmp_path)

    elif adapter_name:
        logging.info(f"Adapter skipped, using base model '{base_model_name}' only.")

    # --- Load model ---
    if current_loaded_model == new_model_to_load:
        return {"status": "already_loaded", "loaded": new_model_to_load}

    try:
        logging.info(f"⚙️ Loading model '{new_model_to_load}' via Ollama API...")
        _ollama_request("POST", "/api/generate", json={
            "model": new_model_to_load,
            "prompt": ".",
            "options": {"num_predict": 1},
            "keep_alive": "5m"
        })
        current_loaded_model = new_model_to_load
        logging.info(f"✅ Model '{new_model_to_load}' is now active.")
        return {"status": "success", "loaded": new_model_to_load}
    except Exception as e:
        logging.error(f"❌ Failed to load model {new_model_to_load}: {e}", exc_info=True)
        if temp_model_name:
            await delete_ollama_model(temp_model_name)
        current_loaded_model = None
        raise HTTPException(status_code=500, detail=f"Failed to load model {new_model_to_load}")


# ----------------------------------------------------------------------
# Run Prompt
# ----------------------------------------------------------------------
async def run_prompt(model_name: str, prompt_text: str, max_tokens: int):
    """Runs a prompt against the specified model."""
    global current_loaded_model

    if not current_loaded_model or current_loaded_model != model_name:
        logging.info(f"Switching active model to {model_name}")
        await set_active_model(model_name, adapter_name=None)

    try:
        logging.info(f"🧩 Running prompt on model: {current_loaded_model}")
        stream = ollama.generate(
            model=current_loaded_model,
            prompt=prompt_text,
            options={'num_predict': max_tokens},
            keep_alive='5m',
            stream=True
        )

        if inspect.isasyncgen(stream):
            async for chunk in stream:
                yield chunk
        else:
            for chunk in stream:
                yield chunk

    except Exception as e:
        logging.error(f"❌ Error running prompt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error running prompt: {e}")
