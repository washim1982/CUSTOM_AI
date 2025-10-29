#!/bin/sh
set -e

echo "Starting Ollama service..."
ollama serve &
pid=$!

echo "Waiting for Ollama to start..."
for i in $(seq 1 30); do
  if nc -z localhost 11434; then
    echo "✅ Ollama is up!"
    break
  fi
  echo "⏳ Waiting for Ollama ($i/30)..."
  sleep 2
done

echo "Pulling models..."
ollama pull granite4:tiny-h || true
ollama pull qwen2.5vl:7b || true
ollama pull llava:latest || true
#ollama pull dolphin-llama3:8b || true
echo "Model pulling complete."

wait $pid
