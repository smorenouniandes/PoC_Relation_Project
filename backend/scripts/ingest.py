"""Script ejecutable: pipeline de ingesta (Paso 2).

Carga las personas sintéticas, consolida cada una en un Perfil de Expertise
Unificado, genera los embeddings (proveedor configurable) y los persiste.

Uso:
    python scripts/ingest.py
    EMBEDDING_PROVIDER=local python scripts/ingest.py   # (por defecto)

Ejecutar desde la carpeta `backend/`.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.paths import ensure_dirs, PERFILES_FILE  # noqa: E402
from app.ingestion.consolidate import construir_perfil_unificado  # noqa: E402
from app.ingestion.repository import cargar_personas, guardar_perfiles  # noqa: E402
from app.providers import get_embedding_provider  # noqa: E402


def main() -> None:
    ensure_dirs()

    print("📥 Cargando personas...")
    personas = cargar_personas()
    print(f"   {len(personas)} personas cargadas.")

    print("🧩 Consolidando perfiles unificados...")
    perfiles = [construir_perfil_unificado(p) for p in personas]

    print("🧠 Inicializando proveedor de embeddings...")
    provider = get_embedding_provider()
    print(f"   Proveedor: {provider.nombre}")

    print("🔢 Generando embeddings (puede tardar la primera vez)...")
    t0 = time.time()
    resumenes = [p.resumen for p in perfiles]
    vectores = provider.embed(resumenes)
    for perfil, vector in zip(perfiles, vectores):
        perfil.embedding = vector
    dt = time.time() - t0

    guardar_perfiles(perfiles)

    print()
    print(f"✅ {len(perfiles)} perfiles unificados con embeddings → {PERFILES_FILE}")
    print(f"   Dimensión de embeddings: {provider.dimension}")
    print(f"   Tiempo de embeddings: {dt:.1f}s")
    print()
    print("   Ejemplo de resumen consolidado (primera persona):")
    print("   " + perfiles[0].resumen[:220] + "...")


if __name__ == "__main__":
    main()
