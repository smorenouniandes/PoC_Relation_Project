"""Estado de la aplicación: carga de datos, motor y feedback.

Centraliza la inicialización (perezosa) para que los routers no la repitan.
En producción, esto se reemplazaría por conexiones a RDS y un servicio de
embeddings/LLM gestionado; la interfaz pública (métodos) no cambiaría.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from app.core.paths import PROCESSED_DIR
from app.ingestion.repository import cargar_personas, cargar_perfiles
from app.matching import MatchingEngine
from app.providers import get_embedding_provider, get_llm_provider


_FEEDBACK_FILE: Path = PROCESSED_DIR / "feedback.json"


class AppState:
    """Contenedor de estado del backend (datos + motor + feedback)."""

    def __init__(self) -> None:
        self.personas = cargar_personas()
        self.perfiles = cargar_perfiles()
        self._personas_by_id = {p.id: p for p in self.personas}
        self.embedding_provider = get_embedding_provider()
        self.llm_provider = get_llm_provider()
        self.engine = MatchingEngine(
            self.personas, self.perfiles,
            self.embedding_provider, self.llm_provider,
        )

    # --- Personas ---
    def persona(self, persona_id: str):
        return self._personas_by_id.get(persona_id)

    # --- Feedback (persistencia simple en archivo para el PoC) ---
    def registrar_feedback(self, consulta: str, persona_id: str,
                           util: bool, comentario: str | None) -> str:
        fid = str(uuid.uuid4())
        registro = {
            "id": fid,
            "consulta": consulta,
            "persona_id": persona_id,
            "util": util,
            "comentario": comentario,
            "fecha": datetime.utcnow().isoformat(),
        }
        data = []
        if _FEEDBACK_FILE.exists():
            data = json.loads(_FEEDBACK_FILE.read_text(encoding="utf-8"))
        data.append(registro)
        _FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        _FEEDBACK_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return fid


# Singleton perezoso
_state: AppState | None = None


def get_state() -> AppState:
    global _state
    if _state is None:
        _state = AppState()
    return _state
