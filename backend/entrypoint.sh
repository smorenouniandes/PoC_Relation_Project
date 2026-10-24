#!/usr/bin/env bash
# Arranque del backend sobre la base de conocimiento FIJA y versionada.
#
# Modelo de datos (gobierno):
#   - Fuente de verdad: data/versioned/${DATA_VERSION}/ (versionada en git).
#   - El runtime NO regenera datos ni recalcula embeddings: consume el dataset
#     congelado y verifica su integridad contra el MANIFEST.json.
#   - Fallback: si la versión no está presente (p. ej. en experimentos locales),
#     se regenera en data/raw + data/processed de forma reproducible.
set -euo pipefail

DATA_VERSION="${DATA_VERSION:-v1}"
VERSIONED_DIR="data/versioned/${DATA_VERSION}"

if [ -f "${VERSIONED_DIR}/perfiles_unificados.json" ]; then
  echo "[entrypoint] Base de conocimiento FIJA detectada: ${VERSIONED_DIR}"
  echo "[entrypoint] Verificando integridad (SHA-256 vs. MANIFEST.json)..."
  # La verificación no debe tumbar el arranque si el manifiesto no está;
  # pero si hay deriva de hashes, lo advertimos claramente.
  if python scripts/verify_dataset.py; then
    echo "[entrypoint] Integridad del dataset OK."
  else
    echo "[entrypoint] ⚠️  Advertencia: el dataset no coincide con el manifiesto."
  fi
else
  echo "[entrypoint] ⚠️  No se encontró el dataset versionado '${DATA_VERSION}'."
  echo "[entrypoint] Fallback: regenerando dataset reproducible (NUM_PERSONAS=${NUM_PERSONAS}, SEED=${SEED})..."
  [ -f "data/raw/personas.json" ] || python scripts/generate_data.py --num "${NUM_PERSONAS}" --seed "${SEED}"
  [ -f "data/processed/perfiles_unificados.json" ] || python scripts/ingest.py
fi

echo "[entrypoint] Iniciando API en 0.0.0.0:8000 (DATA_VERSION=${DATA_VERSION}) ..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000
