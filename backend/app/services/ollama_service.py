# backend/app/services/ollama_service.py
import logging, os, requests, inspect
from fastapi import HTTPException
from typing import Optional, Dict, Any, List

# OLLAMA_HOST like "http://ollama-dev:11434"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")  # You must set this in env
MINIMAX_ENDPOINT = os.getenv(
    "MINIMAX_ENDPOINT",
    "https://api.minimax.chat/v1/text/chatcompletion"
)

GRANITE_MODEL = os.getenv("GRANITE_MODEL", "granite4:tiny-h")


def _ollama_request(method: str, path: str, **kwargs):
    """Helper to call Ollama, raise HTTPException on error."""
    url = f"{OLLAMA_HOST}{path}"
    try:
        r = requests.request(method, url, timeout=60, **kwargs)
    except Exception as e:
        logging.error(f"Ollama request failed: {e}")
        raise HTTPException(status_code=503, detail="Ollama unreachable")

    if not r.ok:
        logging.error(f"Ollama error {r.status_code}: {r.text}")
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return r


def list_local_models() -> List[Dict[str, Any]]:
    """
    Return [{name: 'granite4:tiny-h'}, ...] from Ollama.
    Safe for public use.
    """
    r = _ollama_request("GET", "/api/tags")
    data = r.json()
    out = []
    for m in data.get("models", []):
        name = m.get("name")
        if name:
            out.append({"name": name})
    # We *want* granite to exist. If somehow it's missing, still include it.
    if not any(m["name"] == GRANITE_MODEL for m in out):
        out.insert(0, {"name": GRANITE_MODEL})
    return out


def run_granite_prompt(prompt_text: str, max_tokens: int = 256) -> str:
    """
    Call Ollama /api/generate for granite. Return final text (not streaming).
    """
    body = {
        "model": GRANITE_MODEL,
        "prompt": prompt_text,
        "options": {"num_predict": max_tokens},
        "stream": False,
    }
    r = _ollama_request("POST", "/api/generate", json=body)
    data = r.json()
    # Ollama returns {'response': "..."} for non-stream
    return data.get("response", "").strip()


def run_minimax_prompt(prompt_text: str, max_tokens: int = 256, user: Dict[str,Any] | None = None) -> str:
    """
    Call MiniMax cloud.
    NOTE: You MUST edit this to match the actual MiniMax M2 chat completion API format.
    We'll mock a generic role-based body like OpenAI-style.
    """
    if not MINIMAX_API_KEY:
        # fallback: if not configured, just use granite so UI doesn't break
        logging.warning("MINIMAX_API_KEY not set, falling back to granite.")
        return run_granite_prompt(prompt_text, max_tokens)

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "minimax-m2",  # adjust to your actual MiniMax model name
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(MINIMAX_ENDPOINT, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            logging.error(f"MiniMax error {resp.status_code}: {resp.text}")
            raise HTTPException(status_code=502, detail="MiniMax upstream error")
        data = resp.json()
        # You MUST adapt this path based on real MiniMax response JSON
        # I'll assume data["choices"][0]["message"]["content"]
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return content.strip()
    except requests.RequestException as e:
        logging.error(f"MiniMax request failed: {e}")
        raise HTTPException(status_code=502, detail="MiniMax request failed")


def run_chat(prompt_text: str, max_tokens: int, user: Optional[Dict[str, Any]]) -> str:
    """
    Smart router:
      - no user  -> granite (public)
      - user     -> minimax (private tier)
    """
    if user:
        return run_minimax_prompt(prompt_text, max_tokens, user=user)
    return run_granite_prompt(prompt_text, max_tokens)
