"""Modelos de dominio del PoC Relation Project.

Reflejan las entidades definidas en docs/03-modelo-de-datos.md.
"""

from app.models.entities import (
    FuenteDato,
    Expertise,
    Persona,
    PerfilExpertiseUnificado,
    NivelEvidencia,
    TipoFuente,
    Nivel,
    Disponibilidad,
)

__all__ = [
    "FuenteDato",
    "Expertise",
    "Persona",
    "PerfilExpertiseUnificado",
    "NivelEvidencia",
    "TipoFuente",
    "Nivel",
    "Disponibilidad",
]
