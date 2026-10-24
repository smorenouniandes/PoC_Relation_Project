"""Genera el manifiesto de gobierno de datos del dataset versionado.

Produce `data/versioned/<version>/MANIFEST.json` con la procedencia y las
huellas (hashes) del dataset congelado, para trazabilidad y verificación de
integridad (gobierno de datos). Es idempotente y reproducible.

Uso (desde la carpeta `backend/`):
    python scripts/build_manifest.py --version v1 --num 50 --seed 42

El manifiesto NO recalcula los datos: solo describe y verifica los archivos
ya presentes en la carpeta de la versión.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.paths import VERSIONED_DIR  # noqa: E402
from app.providers.local_embeddings import _DEFAULT_MODEL  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _resumen_personas(data: list[dict]) -> dict:
    niveles = Counter(p["nivel"] for p in data)
    disp = Counter(p["disponibilidad"] for p in data)
    cargos = Counter(p["cargo"] for p in data)
    total_fuentes = sum(len(p.get("fuentes", [])) for p in data)
    total_expertise = sum(len(p.get("expertise", [])) for p in data)
    demostradas = sum(
        1 for p in data for e in p.get("expertise", [])
        if e["nivel_evidencia"] == "PROYECTO"
    )
    return {
        "total_personas": len(data),
        "total_fuentes": total_fuentes,
        "total_senales_expertise": total_expertise,
        "expertise_demostrada_en_proyecto": demostradas,
        "expertise_autodeclarada": total_expertise - demostradas,
        "distribucion_nivel": dict(niveles),
        "distribucion_disponibilidad": dict(disp),
        "distribucion_cargo": dict(cargos),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera el MANIFEST.json de gobierno del dataset versionado."
    )
    parser.add_argument("--version", default="v1", help="Etiqueta de versión (def. v1)")
    parser.add_argument("--num", type=int, default=50, help="NUM_PERSONAS usado al generar")
    parser.add_argument("--seed", type=int, default=42, help="SEED usada al generar")
    parser.add_argument("--embedding-dim", type=int, default=384, help="Dimensión del embedding")
    args = parser.parse_args()

    version_dir = VERSIONED_DIR / args.version
    personas_file = version_dir / "personas.json"
    perfiles_file = version_dir / "perfiles_unificados.json"

    for f in (personas_file, perfiles_file):
        if not f.exists():
            raise FileNotFoundError(
                f"Falta {f}. Genera el dataset antes de construir el manifiesto."
            )

    personas = json.loads(personas_file.read_text(encoding="utf-8"))
    perfiles = json.loads(perfiles_file.read_text(encoding="utf-8"))

    manifest = {
        "dataset": "poc-relation-knowledge-base",
        "version": args.version,
        "descripcion": (
            "Base de conocimiento FIJA y versionada del PoC: perfiles sintéticos "
            "de Ingeniería en banca y sus Perfiles de Expertise Unificados con "
            "embeddings. Dataset congelado y reproducible (no se regenera en runtime)."
        ),
        "naturaleza_datos": "SINTETICOS",  # no contienen PII real
        "generado_en_utc": datetime.now(timezone.utc).isoformat(),
        "reproducibilidad": {
            "generador": "scripts/generate_data.py",
            "ingesta": "scripts/ingest.py",
            "num_personas": args.num,
            "seed": args.seed,
            "determinista": True,
        },
        "embeddings": {
            "proveedor": "local",
            "modelo": _DEFAULT_MODEL,
            "dimension": args.embedding_dim,
            "normalizados": True,
            "nota": (
                "Mismo modelo para indexar perfiles y para vectorizar la consulta "
                "en runtime (mismo espacio vectorial)."
            ),
        },
        "archivos": {
            "personas.json": {
                "sha256": _sha256(personas_file),
                "bytes": personas_file.stat().st_size,
                "registros": len(personas),
            },
            "perfiles_unificados.json": {
                "sha256": _sha256(perfiles_file),
                "bytes": perfiles_file.stat().st_size,
                "registros": len(perfiles),
            },
        },
        "estadisticas": _resumen_personas(personas),
    }

    out = version_dir / "MANIFEST.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Manifiesto escrito → {out}")
    print(f"   personas.json           sha256={manifest['archivos']['personas.json']['sha256'][:16]}…")
    print(f"   perfiles_unificados.json sha256={manifest['archivos']['perfiles_unificados.json']['sha256'][:16]}…")


if __name__ == "__main__":
    main()
