"""Interfaces de proveedores.

El motor de matching depende de estas interfaces, NO de implementaciones
concretas (RNF-11 del doc 02). Así, migrar de embeddings locales a Amazon
Bedrock no requiere tocar la lógica de negocio.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Convierte texto en vectores para búsqueda semántica."""

    @abstractmethod
    def embed(self, textos: list[str]) -> list[list[float]]:
        """Devuelve un embedding por cada texto de entrada."""

    def embed_one(self, texto: str) -> list[float]:
        """Conveniencia: embedding de un solo texto."""
        return self.embed([texto])[0]

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensión de los vectores producidos."""

    @property
    @abstractmethod
    def nombre(self) -> str:
        """Identificador legible del proveedor (para logs/metadatos)."""
