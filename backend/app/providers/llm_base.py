"""Interfaz de proveedor LLM (interpretación de consulta y explicaciones).

El motor de matching depende de esta interfaz, no de una implementación. En el
PoC se usa una implementación local basada en reglas/plantillas; en producción
se sustituye por Amazon Bedrock (Claude) sin tocar la lógica de negocio.

Referencia: docs/04-arquitectura.md §2 (pasos 1 y 4 del pipeline RAG).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class IntencionConsulta:
    """Resultado de interpretar la consulta del usuario (RF-02)."""

    texto_original: str
    habilidades: list[str] = field(default_factory=list)
    nivel: str | None = None          # p. ej. "Senior", si se detecta
    dominio: list[str] = field(default_factory=list)  # dominios de negocio
    es_ambigua: bool = False
    aclaracion_sugerida: str | None = None


class LLMProvider(ABC):
    """Interpreta consultas y genera explicaciones de match."""

    @abstractmethod
    def interpretar(self, consulta: str) -> IntencionConsulta:
        """Extrae intención estructurada de la consulta en lenguaje natural."""

    @abstractmethod
    def explicar_match(self, consulta: str, resumen_persona: str,
                       habilidades_coincidentes: list[str]) -> str:
        """Genera una explicación legible de por qué la persona es buen match (RF-06).

        Debe basarse en evidencia del perfil (sin alucinar — RNF-15).
        """

    @property
    @abstractmethod
    def nombre(self) -> str:
        ...
