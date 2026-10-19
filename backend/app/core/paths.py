"""Rutas base del proyecto (PoC: almacenamiento en archivos)."""

from pathlib import Path

# backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BACKEND_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Archivo con las personas sintéticas generadas (Paso 1)
PERSONAS_FILE = RAW_DIR / "personas.json"


def ensure_dirs() -> None:
    """Crea las carpetas de datos si no existen."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
