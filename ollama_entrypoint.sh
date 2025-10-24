#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

# --- ADD THESE LINES ---
echo "Updating package list and installing curl..."
apt-get update && apt-get install -y curl
echo "curl installed."
# ---------------------

# Start ollama serve in the background
ollama serve &
pid=$!

echo "Waiting for Ollama server to start..."
# Wait until the server is responsive (now curl will work)
while ! curl -s --fail http://localhost:11434 > /dev/null; do
  sleep 1
done
echo "Ollama server started."

# Pull models
echo "Pulling models..."
ollama pull gemma:2b || echo "Failed to pull gemma:2b, continuing..."
ollama pull mistral || echo "Failed to pull mistral, continuing..."
ollama pull codellama:7b || echo "Failed to pull codellama:7b, continuing..."
ollama pull llama3:8b || echo "Failed to pull llama3:8b, continuing..."
ollama pull llava:latest || echo "Failed to pull llava:latest, continuing..."
ollama pull dolphin-llama3:8b || echo "Failed to pull dolphin-llama3:8b, continuing..."
ollama pull deepseek-r1:8b || echo "Failed to pull deepseek-r1:8b, continuing..."
echo "Model pulling complete (or attempted)."

# Bring the background ollama serve process to the foreground
wait $pid