# backend/app/services/ollama_service.py
import ollama
import logging
import os
import tempfile # <--- ADD THIS LINE
import subprocess # <--- Import subprocess
import shutil # Keep for shutil.which check
from fastapi import HTTPException
from typing import Optional, List, Dict, Any # Added List, Dict, Any

logging.basicConfig(level=logging.INFO)

# Check if Ollama CLI exists (optional but good practice for other potential uses)
if shutil.which("ollama") is None:
    logging.warning("Ollama CLI command 'ollama' not found in PATH.")

OLLAMA_LORA_DIR = "/loras" # Path inside Ollama container
BACKEND_LORA_DIR = "/code/loras" # Path inside Backend container
current_loaded_model: str | None = None # Tracks the currently loaded model name (base or combined)

# --- Keep list_local_models ---
def list_local_models():
    """Lists all models available locally in Ollama with detailed logging."""
    try:
        models_data = ollama.list()
        logging.info(f"Ollama raw response (type: {type(models_data)}): {models_data}")

        # Check if the primary key 'models' exists
        if 'models' not in models_data:
            logging.error("Ollama list response is missing 'models' key.")
            return []

        models_list = models_data['models']
        logging.info(f"Extracted models_list (type: {type(models_list)}, length: {len(models_list)}): {models_list}")

        valid_models = []
        if not isinstance(models_list, list):
            logging.error(f"Expected models_list to be a list, but got {type(models_list)}")
            return []

        # Iterate and log each item
        for i, model_item in enumerate(models_list):
            logging.info(f"Processing item {i} (type: {type(model_item)}): {model_item}")
            model_name = None

            # Try accessing attributes/keys based on observed structure
            try:
                if hasattr(model_item, 'model'): # Check for object attribute 'model'
                    model_name = model_item.model
                    logging.info(f"  Item {i} has 'model' attribute: '{model_name}'")
                elif hasattr(model_item, 'name'): # Check for object attribute 'name'
                     model_name = model_item.name
                     logging.info(f"  Item {i} has 'name' attribute: '{model_name}'")
                elif isinstance(model_item, dict): # Check if it's a dictionary
                     model_name = model_item.get('name') # Safely get 'name' key
                     logging.info(f"  Item {i} is dict, name: '{model_name}'")
                else:
                    logging.warning(f"  Item {i} is an unrecognized type or structure.")

                # Add to list if name was found
                if model_name:
                    valid_models.append({"name": model_name})
                    logging.info(f"  Added '{model_name}' to valid_models.")
                else:
                    logging.warning(f"  Could not extract a valid name from item {i}.")

            except Exception as loop_error:
                logging.error(f"  Error processing item {i}: {loop_error}", exc_info=True)

        logging.info(f"Finished processing. Final valid_models list: {valid_models}")
        return valid_models

    except Exception as e:
        logging.error(f"Error in list_local_models (outer scope): {e}", exc_info=True)
        return []

# --- Keep delete_ollama_model ---
async def delete_ollama_model(model_name: str):
    if model_name:
        try:
            logging.info(f"Deleting temporary model: {model_name}")
            ollama.delete(model=model_name)
        except Exception as e:
            logging.warning(f"Could not delete temporary model {model_name}: {e}")

# --- MODIFIED set_active_model ---
async def set_active_model(base_model_name: str, adapter_name: Optional[str] = None):
    """
    Loads base model or applies REAL LoRA via temporary model using Ollama CLI.
    Unloads previous model. Skips placeholder adapters.
    """
    global current_loaded_model
    new_model_to_load = base_model_name
    temp_model_name = None
    apply_adapter = False # Flag to track if we should apply an adapter

    logging.info(f"--- Starting set_active_model (using subprocess CLI) ---")
    logging.info(f"Requested base model: {base_model_name}, Adapter: {adapter_name}")
    logging.info(f"Current loaded model: {current_loaded_model}")

    if adapter_name:
        adapter_path_in_ollama = os.path.join(OLLAMA_LORA_DIR, adapter_name)
        adapter_path_in_backend = os.path.join(BACKEND_LORA_DIR, adapter_name)
        logging.info(f"Checking adapter: {adapter_path_in_backend}")

        if not os.path.exists(adapter_path_in_backend):
             logging.error(f"❌ Adapter file NOT FOUND: {adapter_path_in_backend}")
             raise HTTPException(status_code=404, detail=f"Adapter file '{adapter_name}' not found.")
        else:
             logging.info(f"✅ Adapter file found.")
             # --- Check if it's likely a placeholder ---
             try:
                 file_size = os.path.getsize(adapter_path_in_backend)
                 logging.info(f"Adapter file size: {file_size} bytes")
                 if file_size < 1024 * 1024: # Less than 1MB is almost certainly a placeholder
                     logging.warning(f"⚠️ Adapter '{adapter_name}' is too small, likely a placeholder. Skipping application.")
                     apply_adapter = False # Do not attempt to apply it
                 else:
                     logging.info(f"Adapter size suggests it might be real. Will attempt to apply.")
                     apply_adapter = True # It's large enough, try applying it
             except OSError as e:
                 logging.error(f"❌ Error getting size for adapter file {adapter_path_in_backend}: {e}")
                 raise HTTPException(status_code=500, detail=f"Error accessing adapter file '{adapter_name}'.")

    if apply_adapter:
        temp_model_name = f"{base_model_name}-with-{adapter_name.split('.')[0]}"
        new_model_to_load = temp_model_name
        logging.info(f"Target temporary model name: {temp_model_name}")

        if current_loaded_model == new_model_to_load:
             logging.info(f"Model {new_model_to_load} is already active.")
             return {"status": "already_loaded", "loaded": new_model_to_load}

        modelfile_content = f'''
        FROM {base_model_name}
        ADAPTER {adapter_path_in_ollama}
        '''
        logging.info(f"Generated Modelfile content:\n{modelfile_content}")
        logging.info(f"Attempting to create temporary model '{temp_model_name}' using Ollama CLI...")

        # --- Use temporary file and subprocess ---
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".Modelfile") as temp_modelfile:
                temp_modelfile.write(modelfile_content)
                temp_file_path = temp_modelfile.name

            logging.info(f"Temporary Modelfile created at: {temp_file_path}")

            process = subprocess.run(
                ["ollama", "create", temp_model_name, "-f", temp_file_path],
                check=True, capture_output=True, text=True
            )
            logging.info(f"Ollama CLI stdout: {process.stdout}")
            new_model_to_load = temp_model_name
            logging.info(f"✅ Temporary model '{temp_model_name}' created successfully via CLI.")
        except subprocess.CalledProcessError as e:
            logging.error(f"❌ Failed to create temporary model via Ollama CLI.")
            logging.error(f"Command: {' '.join(e.cmd)}")
            logging.error(f"Return code: {e.returncode}")
            logging.error(f"Stderr: {e.stderr}")
            await delete_ollama_model(temp_model_name) # Attempt cleanup
            # Check for the specific adapter config error
            if "adapter_config.json" in (e.stderr or ""):
                 raise HTTPException(status_code=400, detail=f"Failed to apply adapter '{adapter_name}'. Invalid or missing config.")
            else:
                 raise HTTPException(status_code=500, detail=f"Failed to apply adapter {adapter_name} via CLI: {e.stderr or 'No error output'}")
        except Exception as e:
             logging.error(f"❌ Unexpected error during CLI model creation: {e}", exc_info=True)
             await delete_ollama_model(temp_model_name)
             raise HTTPException(status_code=500, detail=f"Unexpected error applying adapter {adapter_name}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try: os.remove(temp_file_path); logging.info(f"Cleaned up temporary Modelfile: {temp_file_path}")
                except OSError as e: logging.error(f"Error removing temporary Modelfile {temp_file_path}: {e}")
        # ------------------------------------

    elif adapter_name: # Adapter was selected but skipped (placeholder)
         logging.info(f"Adapter '{adapter_name}' was skipped (placeholder). Loading base model '{base_model_name}' instead.")
         new_model_to_load = base_model_name # Ensure we load the base model

    # --- Check if target model (base or temp) is already loaded ---
    if current_loaded_model == new_model_to_load:
        # This condition might be met if adapter was skipped and base was already loaded
        logging.info(f"Target model '{new_model_to_load}' is already active.")
        return {"status": "already_loaded", "loaded": new_model_to_load}

    # --- Unload Previous Model ---
    if current_loaded_model and current_loaded_model != new_model_to_load:
        logging.info(f"Unloading previous model: {current_loaded_model}")
        await delete_ollama_model(current_loaded_model) # Delete previous temp model if exists
        try:
            # Attempt to unload base part via keep_alive=0
            logging.info(f"Attempting keep_alive=0 for base part of: {current_loaded_model}")
            base_part = current_loaded_model.split('-with-')[0]
            available_models_raw = ollama.list()
            available_names = [getattr(m, 'name', m.get('name') if isinstance(m, dict) else None) for m in available_models_raw.get('models', [])]
            if base_part in available_names:
                ollama.generate(model=base_part, prompt=".", options={'num_predict': 1}, keep_alive=0)
                logging.info(f"Unload command sent for {base_part}.")
            else:
                logging.warning(f"Base model {base_part} not found, skipping keep_alive=0 unload.")
        except Exception as unload_e:
            logging.warning(f"Ignoring error during keep_alive=0 unload: {unload_e}")
        current_loaded_model = None # Clear tracker

    # --- Load Target Model ---
    try:
        logging.info(f"Loading target model: {new_model_to_load}")
        try:
            ollama.show(new_model_to_load)
            logging.info(f"Model {new_model_to_load} confirmed to exist by ollama.show.")
        except Exception as show_e:
            logging.error(f"❌ Model {new_model_to_load} does not exist or Ollama error: {show_e}")
            # If it was a temp model that failed creation earlier, it won't exist here
            raise HTTPException(status_code=404, detail=f"Model '{new_model_to_load}' not found by Ollama.")

        ollama.generate(model=new_model_to_load, prompt=".", options={'num_predict': 1}, keep_alive='5m')
        current_loaded_model = new_model_to_load
        logging.info(f"✅ Successfully loaded target model: {new_model_to_load}")
        return {"status": "success", "loaded": new_model_to_load}
    except Exception as e:
        logging.error(f"❌ Failed to load target model {new_model_to_load}: {e}", exc_info=True)
        # Clean up temporary model if its loading failed
        if temp_model_name and temp_model_name == new_model_to_load:
            await delete_ollama_model(temp_model_name)
        current_loaded_model = None # Reset tracker
        raise HTTPException(status_code=500, detail=f"Failed to load model {new_model_to_load}")

# --- Keep run_prompt ---
async def run_prompt(model_name: str, prompt_text: str, max_tokens: int):
    """
    Runs a prompt against the specified model.
    Automatically loads the model if it's not the currently active one.
    """
    global current_loaded_model
    if not current_loaded_model or current_loaded_model != model_name:
        logging.warning(f"Model '{model_name}' requested but '{current_loaded_model}' is loaded. Switching model...")
        try:
            # Assuming set_active_model handles unloading the previous one correctly
            # We only need to load the base model here, no adapter for chatbot/OCR
            await set_active_model(model_name, adapter_name=None)
        except Exception as load_exc:
            # Handle potential errors during the automatic switch
            logging.error(f"Automatic model switch to '{model_name}' failed: {load_exc}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to switch to model '{model_name}'.")
    # --- END MODIFICATION ---
    try:
        #stream = ollama.generate(model=current_loaded_model, prompt=prompt_text, options={'num_predict': max_tokens}, keep_alive='5m', stream=True)
        logging.info(f"Running prompt on currently loaded model: {current_loaded_model}")
        stream = ollama.generate(
            model=current_loaded_model, # Use the confirmed loaded model
            prompt=prompt_text,
            options={'num_predict': max_tokens},
            keep_alive='5m',
            stream=True
        )
        return stream
    except Exception as e:
        logging.error(f"Error running prompt on model {current_loaded_model}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing your request.")