# backend/Dockerfile

# 1. Use an official NVIDIA CUDA base image compatible with modern GPUs
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

# 2. Set up the environment and install Python
ENV PYTHON_VERSION=3.11
RUN apt-get update && apt-get install -y \
    python${PYTHON_VERSION} \
    python3-pip \
    build-essential libffi-dev python3-dev \
    sqlite3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

    
# Install system packages + Ollama CLI
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y python3 python3-pip git curl && \
    curl -fsSL https://ollama.com/install.sh | sh


# --- Stage 2: Final Image ---
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

ENV PYTHON_VERSION=3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION} \
    python3-pip \
    libffi7 \
    sqlite3 \ 
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Check ollama version (optional)
RUN pip install --no-cache-dir ollama==0.6.0

# Set python3.11 as the default python command
RUN update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1

WORKDIR /code

# 3. Copy and install Python requirements
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# 4. Expose the port and run the application
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]