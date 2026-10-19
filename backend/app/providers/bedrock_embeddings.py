"""Proveedor de embeddings para PRODUCCIÓN: Amazon Bedrock (Titan Embeddings).

NO se usa en el PoC local (no hay credenciales AWS aquí). Se incluye como
referencia del camino a producción y para dejar la factory completa. La
implementación real requiere `boto3` y permisos sobre Bedrock.

Mantiene la MISMA interfaz que LocalEmbeddingProvider, por lo que el resto del
sistema no cambia al migrar.
"""

from __future__ import annotations

from app.providers.base import EmbeddingProvider

# Modelo de embeddings de Amazon Bedrock (ejemplo).
_DEFAULT_MODEL_ID = "amazon.titan-embed-text-v2:0"
_DEFAULT_DIMENSION = 1024


class BedrockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_id: str = _DEFAULT_MODEL_ID, region: str = "us-east-1"):
        self._model_id = model_id
        self._region = region
        self._client = None

    def _ensure_client(self):
        if self._client is None:
            try:
                import boto3  # noqa: F401
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "BedrockEmbeddingProvider requiere 'boto3'. Instálalo y "
                    "configura credenciales AWS para usarlo en producción."
                ) from exc
            import boto3

            self._client = boto3.client("bedrock-runtime", region_name=self._region)
        return self._client

    def embed(self, textos: list[str]) -> list[list[float]]:  # pragma: no cover
        import json

        client = self._ensure_client()
        vectores: list[list[float]] = []
        for texto in textos:
            resp = client.invoke_model(
                modelId=self._model_id,
                body=json.dumps({"inputText": texto}),
            )
            payload = json.loads(resp["body"].read())
            vectores.append(payload["embedding"])
        return vectores

    @property
    def dimension(self) -> int:
        return _DEFAULT_DIMENSION

    @property
    def nombre(self) -> str:
        return f"bedrock:{self._model_id}"
