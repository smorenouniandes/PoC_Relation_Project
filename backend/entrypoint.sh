#!/usr/bin/env bash
# Prepara los datos del PoC (si no existen) y arranca la API.
# Idempotente: no regenera si los archivos ya están presentes.
set -euo pipefail

PERSONAS_FILE="data/raw/personas.json"
PERFILES_FILE="data/processed/perfiles_unificados.json"

if [ ! -f "$PERSONAS_FILE" ]; then
  echo "[entrypoint] Generando datos sintéticos (NUM_PERSONAS=${NUM_PERSONAS}, SEED=${SEED})..."
  python scripts/generate_data.py --num "${NUM_PERSONAS}" --seed "${SEED}"
else
  echo "[entrypoint] Datos sintéticos ya presentes, se omite generación."
fi

if [ ! -f "$PERFILES_FILE" ]; then
  echo "[entrypoint] Ejecutando ingesta (consolidación + embeddings)..."
  python scripts/ingest.py
else
  echo "[entrypoint] Perfiles unificados ya presentes, se omite ingesta."
fi

echo "[entrypoint] Iniciando API en 0.0.0.0:8000 ..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000
