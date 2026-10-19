# Backend — PoC Relation Project
# Imagen de Python con FastAPI + sentence-transformers.
FROM python:3.11-slim

# Evita prompts y bytecode .pyc; logs sin buffer.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dependencias del sistema mínimas (compilación de algunas ruedas).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias primero (mejor cacheo de capas).
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código de la aplicación.
COPY app ./app
COPY scripts ./scripts
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Variables por defecto (sobrescribibles en compose).
ENV EMBEDDING_PROVIDER=local \
    LLM_PROVIDER=local \
    NUM_PERSONAS=50 \
    SEED=42

EXPOSE 8000

# El entrypoint prepara los datos (si faltan) y levanta la API.
ENTRYPOINT ["./entrypoint.sh"]
