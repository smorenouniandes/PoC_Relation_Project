"""Schemas Pydantic: contratos de entrada/salida de la API.

Separar los schemas de las entidades de dominio permite evolucionar la API sin
acoplarla al modelo interno (facilita futuras modificaciones).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Búsqueda
# --------------------------------------------------------------------------- #
class BuscarRequest(BaseModel):
    consulta: str = Field(..., min_length=1, description="Necesidad en lenguaje natural")
    top_k: int = Field(5, ge=1, le=20, description="Máximo de resultados")


class IntencionOut(BaseModel):
    texto_original: str
    habilidades: list[str] = []
    nivel: str | None = None
    dominio: list[str] = []
    es_ambigua: bool = False
    aclaracion_sugerida: str | None = None


class PersonaResumenOut(BaseModel):
    id: str
    nombre: str
    cargo: str
    nivel: str
    area: str
    ubicacion: str
    correo_corporativo: str
    disponibilidad: str


class RecomendacionOut(BaseModel):
    persona: PersonaResumenOut
    score: float
    nivel_confianza: str
    explicacion: str
    habilidades_coincidentes: list[str] = []
    detalle_score: dict = {}


class BuscarResponse(BaseModel):
    consulta: str
    intencion: IntencionOut
    total: int
    recomendaciones: list[RecomendacionOut]
    mensaje: str | None = None  # p. ej. aviso de ambigüedad o sin resultados


# --------------------------------------------------------------------------- #
# Feedback
# --------------------------------------------------------------------------- #
class FeedbackRequest(BaseModel):
    consulta: str
    persona_id: str
    util: bool
    comentario: str | None = None


class FeedbackResponse(BaseModel):
    registrado: bool
    id: str


# --------------------------------------------------------------------------- #
# Personas
# --------------------------------------------------------------------------- #
class FuenteOut(BaseModel):
    tipo: str
    contenido_texto: str
    fecha: str


class ExpertiseOut(BaseModel):
    habilidad: str
    categoria: str
    nivel_evidencia: str


class PersonaDetalleOut(PersonaResumenOut):
    visible: bool
    fecha_actualizacion: str
    fuentes: list[FuenteOut] = []
    expertise: list[ExpertiseOut] = []


# --------------------------------------------------------------------------- #
# Metadatos / salud
# --------------------------------------------------------------------------- #
class SaludOut(BaseModel):
    estado: str
    personas_cargadas: int
    perfiles_cargados: int
    proveedor_embeddings: str
    proveedor_llm: str


class HabilidadOut(BaseModel):
    habilidad: str
    categoria: str


class EstadisticasOut(BaseModel):
    total_personas: int
    por_cargo: dict[str, int]
    por_nivel: dict[str, int]
    por_disponibilidad: dict[str, int]
    total_habilidades_unicas: int
