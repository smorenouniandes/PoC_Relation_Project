"""Verifica la integridad de la base de conocimiento FIJA versionada.

Gobierno de datos: recalcula los hashes SHA-256 de los archivos del dataset
activo y los compara contra el MANIFEST.json. Falla (exit 1) si hay deriva,
lo que delata una edición no controlada del dataset "congelado".

Uso (desde la carpeta `backend/`):
    python scripts/verify_dataset.py            # versión activa (DATA_VERSION)
    DATA_VERSION=v1 python scripts/verify_dataset.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.paths import (  # noqa: E402
    ACTIVE_DATASET_DIR,
    DATA_VERSION,
    VERSIONED_MANIFEST_FILE,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not VERSIONED_MANIFEST_FILE.exists():
        print(f"❌ No existe el manifiesto: {VERSIONED_MANIFEST_FILE}")
        return 1

    manifest = json.loads(VERSIONED_MANIFEST_FILE.read_text(encoding="utf-8"))
    print(f"🔎 Verificando dataset '{manifest.get('dataset')}' versión '{DATA_VERSION}'...")

    ok = True
    for nombre, meta in manifest.get("archivos", {}).items():
        ruta = ACTIVE_DATASET_DIR / nombre
        if not ruta.exists():
            print(f"   ❌ Falta {nombre}")
            ok = False
            continue
        real = _sha256(ruta)
        esperado = meta["sha256"]
        if real == esperado:
            print(f"   ✅ {nombre}  sha256 OK")
        else:
            print(f"   ❌ {nombre}  sha256 NO coincide")
            print(f"      esperado: {esperado}")
            print(f"      real:     {real}")
            ok = False

    if ok:
        print("✅ Integridad verificada: el dataset coincide con el manifiesto.")
        return 0
    print("❌ Integridad COMPROMETIDA: el dataset difiere del manifiesto.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
