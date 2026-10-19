"""Script ejecutable: genera datos sintéticos y los guarda en data/raw/.

Uso:
    python scripts/generate_data.py --num 50 --seed 42

Ejecutar desde la carpeta `backend/`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Permitir ejecutar el script directamente (añade backend/ al path)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.paths import PERSONAS_FILE, ensure_dirs  # noqa: E402
from app.data_generation import generar_personas  # noqa: E402
from app.models.entities import to_serializable  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera personas sintéticas para el PoC de relacionamiento."
    )
    parser.add_argument("--num", type=int, default=50, help="Número de personas (def. 50)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla (def. 42)")
    args = parser.parse_args()

    ensure_dirs()
    personas = generar_personas(num=args.num, seed=args.seed)

    data = [to_serializable(p) for p in personas]
    PERSONAS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Resumen para la consola
    total_fuentes = sum(len(p.fuentes) for p in personas)
    total_expertise = sum(len(p.expertise) for p in personas)
    demostradas = sum(
        1 for p in personas for e in p.expertise
        if e.nivel_evidencia.value == "PROYECTO"
    )

    print(f"✅ Generadas {len(personas)} personas → {PERSONAS_FILE}")
    print(f"   Fuentes de datos:   {total_fuentes}")
    print(f"   Señales de expertise: {total_expertise} "
          f"({demostradas} demostradas en proyecto, "
          f"{total_expertise - demostradas} autodeclaradas)")
    print()
    print("   Ejemplo (primera persona):")
    p0 = personas[0]
    print(f"   • {p0.nombre} — {p0.cargo} ({p0.nivel.value}) · {p0.ubicacion}")
    print(f"     {p0.correo_corporativo} · {p0.disponibilidad.value}")
    print(f"     Habilidades: {', '.join(sorted({e.habilidad for e in p0.expertise}))}")


if __name__ == "__main__":
    main()
