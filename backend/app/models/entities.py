"""Entidades de dominio.

Implementadas como dataclasses para mantener el PoC ligero y sin dependencias
pesadas. En producción podrían mapearse a modelos ORM (SQLAlchemy) o Pydantic.
Referencia: docs/03-modelo-de-datos.md
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


# --------------------------------------------------------------------------- #
# Enumeraciones
# --------------------------------------------------------------------------- #
class TipoFuente(str, Enum):
    CV = "CV"
    CARGO = "CARGO"
    DESCRIPCION = "DESCRIPCION"
    PROYECTO = "PROYECTO"
    # Fuentes de Fase 2 (fuera del alcance del PoC):
    TICKET = "TICKET"
    CORREO = "CORREO"


class NivelEvidencia(str, Enum):
    """Qué tan fuerte es la evidencia de una habilidad (doc 03, RF-07)."""

    AUTODECLARADO = "AUTODECLARADO"  # p. ej. mencionado en CV/descripción
    PROYECTO = "PROYECTO"            # demostrado en un proyecto real
    TICKET = "TICKET"               # resuelto en un ticket (Fase 2)


class Nivel(str, Enum):
    JUNIOR = "Junior"
    SEMI_SENIOR = "Semi-Senior"
    SENIOR = "Senior"
    LIDER = "Líder"


class Disponibilidad(str, Enum):
    DISPONIBLE = "Disponible"
    OCUPADO = "Ocupado"


def _new_id() -> str:
    return str(uuid.uuid4())


# --------------------------------------------------------------------------- #
# Entidades
# --------------------------------------------------------------------------- #
@dataclass
class FuenteDato:
    """Un documento/origen crudo asociado a una persona (doc 03 §3.2)."""

    persona_id: str
    tipo: TipoFuente
    contenido_texto: str
    uri_original: str = ""
    fecha: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=_new_id)


@dataclass
class Expertise:
    """Señal atómica de habilidad con su evidencia (doc 03 §3.3)."""

    persona_id: str
    habilidad: str
    categoria: str  # Tecnología / Dominio de negocio / Metodología / Herramienta
    nivel_evidencia: NivelEvidencia
    fuente_id: Optional[str] = None
    recencia: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=_new_id)


@dataclass
class Persona:
    """Persona de la organización (doc 03 §3.1)."""

    nombre: str
    correo_corporativo: str
    area: str
    cargo: str
    nivel: Nivel
    ubicacion: str = ""
    disponibilidad: Disponibilidad = Disponibilidad.DISPONIBLE
    visible: bool = True  # opt-in para ser recomendado (Fase 2)
    fecha_actualizacion: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=_new_id)

    # Relaciones (se llenan en memoria; en BD serían tablas aparte)
    fuentes: list[FuenteDato] = field(default_factory=list)
    expertise: list[Expertise] = field(default_factory=list)


@dataclass
class PerfilExpertiseUnificado:
    """Consolidación por persona, base del embedding (doc 03 §3.4).

    Se genera en el Paso 2 (ingesta). Aquí se define para completar el modelo.
    """

    persona_id: str
    resumen: str
    habilidades_clave: list[str] = field(default_factory=list)
    embedding: Optional[list[float]] = None
    fecha_generacion: datetime = field(default_factory=datetime.utcnow)


# --------------------------------------------------------------------------- #
# Serialización auxiliar
# --------------------------------------------------------------------------- #
def to_serializable(obj) -> dict:
    """Convierte una dataclass a dict JSON-serializable (enums y datetimes)."""

    def _convert(value):
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, list):
            return [_convert(v) for v in value]
        if isinstance(value, dict):
            return {k: _convert(v) for k, v in value.items()}
        return value

    return {k: _convert(v) for k, v in asdict(obj).items()}
