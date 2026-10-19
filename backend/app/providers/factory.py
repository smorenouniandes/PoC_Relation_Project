"""Factory de proveedores: elige la implementación según configuración.

Variable de entorno `EMBEDDING_PROVIDER`:
    - "local"   -> LocalEmbeddingProvider (sentence-transformers)  [PoC, por defecto]
    - "bedrock" -> BedrockEmbeddingProvider (Amazon Bedrock)       [producción]

Así el mismo código corre en el PoC y en AWS sin cambios en la lógica.
"""

from __future__ import annotations

import os

from app.providers.base import EmbeddingProvider


def get_embedding_provider(nombre: str | None = None) -> EmbeddingProvider:
    nombre = (nombre or os.getenv("EMBEDDING_PROVIDER", "local")).lower()

    if nombre == "local":
        from app.providers.local_embeddings import LocalEmbeddingProvider

        return LocalEmbeddingProvider()

    if nombre == "bedrock":
        from app.providers.bedrock_embeddings import BedrockEmbeddingProvider

        return BedrockEmbeddingProvider()

    raise ValueError(
        f"Proveedor de embeddings desconocido: '{nombre}'. "
        "Usa 'local' o 'bedrock'."
    )
