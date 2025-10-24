# backend/app/services/training_service.py
import subprocess
import ollama
import logging
import random
import tempfile
import os
import shutil
from typing import Dict, List, Any, Optional
from fastapi import UploadFile

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)

# --- Check if Ollama CLI exists ---
if shutil.which("ollama") is None:
    logging.error("❌ Ollama CLI command 'ollama' not found in PATH. Subprocess calls will fail.")
    # Consider raising an error here


LORA_DIR = "/code/loras"

def generate_sql_training_data(schema: dict, num_examples: int) -> list:
    """
    Generates synthetic SQL QA pairs from a database schema.
    """
    qa_pairs = []
    logging.info(f"Received training file: {list(schema.keys())}")
    tables = list(schema.keys())
    logging.info(f"Received training file: {tables}")

    if not tables:
        return []

    for _ in range(num_examples):
        table = random.choice(tables)
        columns = schema[table]
        
        # Simple SELECT
        question = f"Show me all data from the {table} table."
        answer = f"SELECT * FROM {table};"
        qa_pairs.append({"question": question, "answer": answer})

        # SELECT with a filter
        if columns:
            col = random.choice(columns)
            question = f"Find all records in {table} where {col} is 'some_value'."
            answer = f"SELECT * FROM {table} WHERE {col} = 'some_value';"
            qa_pairs.append({"question": question, "answer": answer})

        # AGGREGATE function
        numeric_cols = [c for c in columns if "id" in c or "amount" in c or "count" in c]
        if numeric_cols:
            agg_col = random.choice(numeric_cols)
            agg_func = random.choice(["SUM", "AVG", "COUNT"])
            question = f"What is the {agg_func.lower()} of {agg_col} in the {table} table?"
            answer = f"SELECT {agg_func}({agg_col}) FROM {table};"
            qa_pairs.append({"question": question, "answer": answer})
            
    return qa_pairs


# --- THIS IS THE MISSING FUNCTION ---

def _simulate_lora_training(base_model: str, custom_adapter_name: str, source_info: str) -> str:
    """Simulates LoRA training by creating a placeholder file."""
    # Ensure name has a standard LoRA extension
    if not any(custom_adapter_name.endswith(ext) for ext in [".safetensors", ".bin", ".pt"]):
        custom_adapter_name += ".safetensors" # Default extension

    adapter_path = os.path.join(LORA_DIR, custom_adapter_name)

    # Create a small placeholder file
    try:
        with open(adapter_path, "w") as f:
            f.write(f"Placeholder LoRA trained from {base_model} using {source_info}.\n")
            f.write("This is not a real adapter file.\n")
        logging.info(f"✅ Simulated LoRA training. Placeholder created: {custom_adapter_name}")
        return custom_adapter_name # Return the filename
    except Exception as e:
        logging.error(f"❌ Failed to create placeholder LoRA file: {e}", exc_info=True)
        raise RuntimeError(f"Failed to simulate LoRA training for {custom_adapter_name}") from e


def train_sql_lora_adapter( # Renamed function
    base_model: str,
    custom_model_name: str, # We'll use this for the adapter name
    qa_data: List[Dict[str, str]]
):
    """Simulates training a SQL LoRA adapter."""
    # Use _simulate_lora_training
    adapter_filename = _simulate_lora_training(base_model, custom_model_name, "generated SQL QA data")
    return {"status": "success", "adapter_filename": adapter_filename}


def train_lora_adapter_from_file( # Renamed function
    base_model: str,
    custom_model_name: str, # We'll use this for the adapter name
    training_file: UploadFile
):
    """Simulates training a LoRA adapter from an uploaded file."""
    # Use _simulate_lora_training
    adapter_filename = _simulate_lora_training(base_model, custom_model_name, f"file {training_file.filename}")
    return {"status": "success", "adapter_filename": adapter_filename}

def create_custom_model_from_data(
    base_model: str,
    custom_model_name: str,
    training_file: Optional[UploadFile] = None,
    qa_data: Optional[List[Dict[str, str]]] = None
):
    """
    Creates a custom model using the Ollama CLI via subprocess.
    Uses best practices for temporary files and error handling.
    """
    # --- Step 1: Build Modelfile Content ---
    # (Your existing logic for building modelfile_content remains the same)
    if qa_data:
        modelfile_content = f"""FROM {base_model}
SYSTEM \"\"\"You are a specialized SQL assistant. Answer the user's question by generating a valid SQL query based on the examples provided.\"\"\"
"""
        for pair in qa_data:
            question = pair.get("question", "").replace('"""', '\\"""')
            answer = pair.get("answer", "").replace('"""', '\\"""')
            modelfile_content += f'\nMESSAGE user """{question}"""'
            modelfile_content += f'\nMESSAGE assistant """{answer}"""'
    elif training_file:
        # Placeholder: Implement actual file parsing here
        logging.info(f"Received training file: {training_file.filename} (Parsing not implemented)")
        modelfile_content = f"""FROM {base_model}
SYSTEM "You are a specialized assistant trained on the content of {training_file.filename}."
"""
    else:
        modelfile_content = f"""FROM {base_model}
SYSTEM "You are a helpful assistant."
"""

    # --- Step 2: Use a temporary file safely ---
    # `tempfile.NamedTemporaryFile` ensures the file is automatically cleaned up
    try:
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".Modelfile") as temp_modelfile:
            temp_modelfile.write(modelfile_content)
            temp_file_path = temp_modelfile.name # Get the path

        logging.info(f"Temporary Modelfile created at: {temp_file_path}")

        # --- Step 3: Run Ollama CLI command ---
        # Best practice: Capture stderr for better error messages
        process = subprocess.run(
            ["ollama", "create", custom_model_name, "-f", temp_file_path],
            check=True, # Raises CalledProcessError on failure
            capture_output=True, # Capture stdout and stderr
            text=True # Decode stdout/stderr as text
        )
        logging.info(f"Ollama CLI stdout: {process.stdout}") # Log success output

        # --- Step 4: Success ---
        logging.info(f"✅ Successfully created custom model: {custom_model_name}")
        return {"status": "success", "model_name": custom_model_name}

    except subprocess.CalledProcessError as e:
        # Best practice: Log the specific error output from the CLI command
        logging.error(f"❌ Failed to create model via Ollama CLI.")
        logging.error(f"Command: {' '.join(e.cmd)}")
        logging.error(f"Return code: {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
        # Raise a more informative error
        raise RuntimeError(f"Model creation via Ollama CLI failed: {e.stderr or 'No error output'}") from e
    except Exception as e:
        # Catch any other unexpected errors
        logging.error(f"❌ An unexpected error occurred during model creation: {e}", exc_info=True)
        raise RuntimeError("An unexpected error occurred during model creation") from e

    finally:
        # --- Step 5: Ensure temporary file cleanup ---
        # The 'with' statement handles this, but an extra check can be added
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logging.info(f"Cleaned up temporary Modelfile: {temp_file_path}")
            except OSError as e:
                logging.error(f"Error removing temporary Modelfile {temp_file_path}: {e}")