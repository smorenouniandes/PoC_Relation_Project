"""Carga/guardado de datos del PoC en archivos JSON.

Encapsula la persistencia para que el resto del código no dependa del formato
de almacenamiento. En producción, estas funciones se reimplementan contra
RDS (PostgreSQL + pgvector) sin cambiar a los llamadores.
"""

from __future__ import annotations

import json
from datetime import datetime

from app.core.paths import PERSONAS_FILE, PERFILES_FILE
from app.models.entities import (
    Persona,
    FuenteDato,
    Expertise,
    PerfilExpertiseUnificado,
    TipoFuente,
    NivelEvidencia,
    Nivel,
    Disponibilidad,
)


def _parse_dt(valor: str) -> datetime:
    return datetime.fromisoformat(valor)


def cargar_personas() -> list[Persona]:
    """Lee las personas sintéticas desde data/raw/personas.json."""
    if not PERSONAS_FILE.exists():
        raise FileNotFoundError(
            f"No existe {PERSONAS_FILE}. Ejecuta primero scripts/generate_data.py"
        )
    data = json.loads(PERSONAS_FILE.read_text(encoding="utf-8"))
    personas: list[Persona] = []
    for d in data:
        fuentes = [
            FuenteDato(
                persona_id=f["persona_id"],
                tipo=TipoFuente(f["tipo"]),
                contenido_texto=f["contenido_texto"],
                uri_original=f.get("uri_original", ""),
                fecha=_parse_dt(f["fecha"]),
                id=f["id"],
            )
            for f in d.get("fuentes", [])
        ]
        expertise = [
            Expertise(
                persona_id=e["persona_id"],
                habilidad=e["habilidad"],
                categoria=e["categoria"],
                nivel_evidencia=NivelEvidencia(e["nivel_evidencia"]),
                fuente_id=e.get("fuente_id"),
                recencia=_parse_dt(e["recencia"]),
                id=e["id"],
            )
            for e in d.get("expertise", [])
        ]
        personas.append(
            Persona(
                nombre=d["nombre"],
                correo_corporativo=d["correo_corporativo"],
                area=d["area"],
                cargo=d["cargo"],
                nivel=Nivel(d["nivel"]),
                ubicacion=d.get("ubicacion", ""),
                disponibilidad=Disponibilidad(d["disponibilidad"]),
                visible=d.get("visible", True),
                fecha_actualizacion=_parse_dt(d["fecha_actualizacion"]),
                id=d["id"],
                fuentes=fuentes,
                expertise=expertise,
            )
        )
    return personas


def guardar_perfiles(perfiles: list[PerfilExpertiseUnificado]) -> None:
    """Persiste los Perfiles de Expertise Unificados (con embeddings)."""
    data = [
        {
            "persona_id": p.persona_id,
            "resumen": p.resumen,
            "habilidades_clave": p.habilidades_clave,
            "embedding": p.embedding,
            "fecha_generacion": p.fecha_generacion.isoformat(),
        }
        for p in perfiles
    ]
    PERFILES_FILE.write_text(
        json.dumps(data, ensure_ascii=False), encoding="utf-8"
    )


def cargar_perfiles() -> list[PerfilExpertiseUnificado]:
    """Lee los Perfiles de Expertise Unificados persistidos."""
    if not PERFILES_FILE.exists():
        raise FileNotFoundError(
            f"No existe {PERFILES_FILE}. Ejecuta primero scripts/ingest.py"
        )
    data = json.loads(PERFILES_FILE.read_text(encoding="utf-8"))
    return [
        PerfilExpertiseUnificado(
            persona_id=d["persona_id"],
            resumen=d["resumen"],
            habilidades_clave=d["habilidades_clave"],
            embedding=d["embedding"],
            fecha_generacion=_parse_dt(d["fecha_generacion"]),
        )
        for d in data
    ]
