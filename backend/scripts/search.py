"""Script ejecutable: busca expertos por consulta en lenguaje natural (Paso 3).

Uso:
    # Consulta única:
    python scripts/search.py "ayuda con optimización de PostgreSQL en reportería"

    # Modo interactivo (sin argumentos):
    python scripts/search.py

Ejecutar desde la carpeta `backend/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingestion.repository import cargar_personas, cargar_perfiles  # noqa: E402
from app.matching import MatchingEngine  # noqa: E402
from app.providers import get_embedding_provider, get_llm_provider  # noqa: E402


def _imprimir_resultados(intencion, recomendaciones) -> None:
    if intencion.es_ambigua:
        print(f"\n🤔 Tu consulta es ambigua. {intencion.aclaracion_sugerida}\n")
        return

    if intencion.habilidades or intencion.dominio:
        detectado = ", ".join(intencion.habilidades + intencion.dominio)
        print(f"   (detecté: {detectado})")

    if not recomendaciones:
        print("\n❌ No encontré personas con un match razonable para tu consulta.")
        print("   (registrado como posible brecha de conocimiento)\n")
        return

    print(f"\n✅ Personas recomendadas:\n")
    for i, r in enumerate(recomendaciones, 1):
        p = r.persona
        print(f"{i}. {p.nombre} · {p.cargo} ({p.nivel.value}) · {p.ubicacion}")
        print(f"   Confianza: {r.nivel_confianza}  (score {r.score})")
        print(f"   Por qué: {r.explicacion}")
        print(f"   📧 {p.correo_corporativo}  ·  {p.disponibilidad.value}")
        print()


def _construir_engine() -> MatchingEngine:
    personas = cargar_personas()
    perfiles = cargar_perfiles()
    emb = get_embedding_provider()
    llm = get_llm_provider()
    return MatchingEngine(personas, perfiles, emb, llm)


def main() -> None:
    engine = _construir_engine()

    # Modo consulta única
    if len(sys.argv) > 1:
        consulta = " ".join(sys.argv[1:])
        print(f"🔎 Consulta: {consulta}")
        intencion, recs = engine.buscar(consulta)
        _imprimir_resultados(intencion, recs)
        return

    # Modo interactivo
    print("💬 Buscador de expertos (PoC). Escribe tu necesidad o 'salir'.\n")
    while True:
        try:
            consulta = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if consulta.lower() in {"salir", "exit", "quit", ""}:
            break
        intencion, recs = engine.buscar(consulta)
        _imprimir_resultados(intencion, recs)


if __name__ == "__main__":
    main()
