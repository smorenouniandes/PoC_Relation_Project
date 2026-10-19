"""Proveedor de embeddings LOCAL para el PoC (sentence-transformers).

Usa un modelo multilingüe para que el español funcione bien. El modelo se
carga de forma perezosa (lazy) la primera vez que se usa.

En producción se sustituye por un BedrockEmbeddingProvider (Titan Embeddings)
que implemente la misma interfaz.
"""

from __future__ import annotations

from app.providers.base import EmbeddingProvider

# Modelo multilingüe compacto y de buena calidad para ES.
_DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class LocalEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = _DEFAULT_MODEL):
        self._model_name = model_name
        self._model = None  # carga perezosa
        self._dimension = 384  # dimensión del modelo por defecto

    def _ensure_model(self):
        if self._model is None:
            # Import local para no exigir la dependencia salvo que se use.
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
            # Compatibilidad: el método fue renombrado en versiones recientes.
            if hasattr(self._model, "get_embedding_dimension"):
                self._dimension = self._model.get_embedding_dimension()
            else:  # versiones antiguas
                self._dimension = self._model.get_sentence_embedding_dimension()
        return self._model

    def embed(self, textos: list[str]) -> list[list[float]]:
        model = self._ensure_model()
        vectores = model.encode(
            textos,
            normalize_embeddings=True,  # facilita similitud por producto punto
            show_progress_bar=False,
        )
        return [v.tolist() for v in vectores]

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def nombre(self) -> str:
        return f"local:{self._model_name}"
