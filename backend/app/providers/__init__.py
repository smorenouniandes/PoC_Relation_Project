"""Capa de abstracción de proveedores (LLM / embeddings).

Permite que el PoC corra con implementaciones locales mientras producción usa
Amazon Bedrock, cambiando solo el proveedor por configuración.
"""

from app.providers.base import EmbeddingProvider
from app.providers.llm_base import LLMProvider, IntencionConsulta
from app.providers.local_embeddings import LocalEmbeddingProvider
from app.providers.local_llm import LocalLLMProvider
from app.providers.factory import get_embedding_provider, get_llm_provider

__all__ = [
    "EmbeddingProvider",
    "LLMProvider",
    "IntencionConsulta",
    "LocalEmbeddingProvider",
    "LocalLLMProvider",
    "get_embedding_provider",
    "get_llm_provider",
]
