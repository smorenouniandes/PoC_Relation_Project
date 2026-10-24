"""Rutas base del proyecto (PoC: almacenamiento en archivos).

Gobierno de datos
-----------------
La **base de conocimiento es FIJA y versionada**: vive bajo
`data/versioned/<version>/` y se versiona en git (es la fuente de verdad que
consume la API en runtime). Las carpetas `data/raw/` y `data/processed/` son
un **área de trabajo efímera** para quien quiera regenerar el dataset; no se
versionan.

La versión activa se controla con la variable de entorno `DATA_VERSION`
(por defecto `v1`). Para "congelar" otro dataset, se genera una carpeta
`data/versioned/<nueva>/` y se apunta `DATA_VERSION` a ella.
"""

import os
from pathlib import Path

# backend/
BACKEND_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BACKEND_DIR / "data"

# --- Área de trabajo efímera (regeneración; NO versionada) ---
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Salidas de los scripts de regeneración (efímeras).
PERSONAS_FILE = RAW_DIR / "personas.json"
PERFILES_FILE = PROCESSED_DIR / "perfiles_unificados.json"

# --- Base de conocimiento FIJA y versionada (fuente de verdad) ---
VERSIONED_DIR = DATA_DIR / "versioned"

# Versión activa del dataset (configurable por entorno).
DATA_VERSION = os.getenv("DATA_VERSION", "v1")

# Archivos del dataset congelado de la versión activa.
ACTIVE_DATASET_DIR = VERSIONED_DIR / DATA_VERSION
VERSIONED_PERSONAS_FILE = ACTIVE_DATASET_DIR / "personas.json"
VERSIONED_PERFILES_FILE = ACTIVE_DATASET_DIR / "perfiles_unificados.json"
VERSIONED_MANIFEST_FILE = ACTIVE_DATASET_DIR / "MANIFEST.json"


def ensure_dirs() -> None:
    """Crea las carpetas de datos efímeras si no existen (para regeneración)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def personas_source() -> Path:
    """Ruta de personas a consumir en runtime.

    Prioriza el dataset FIJO versionado (fuente de verdad). Si no existe esa
    versión pero sí hay datos regenerados localmente, usa estos últimos como
    respaldo (útil al experimentar).
    """
    if VERSIONED_PERSONAS_FILE.exists():
        return VERSIONED_PERSONAS_FILE
    return PERSONAS_FILE


def perfiles_source() -> Path:
    """Ruta de perfiles unificados a consumir en runtime (ver `personas_source`)."""
    if VERSIONED_PERFILES_FILE.exists():
        return VERSIONED_PERFILES_FILE
    return PERFILES_FILE
