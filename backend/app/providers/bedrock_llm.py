"""Proveedor LLM para PRODUCCIÓN: Amazon Bedrock (Claude).

NO se usa en el PoC local (sin credenciales AWS). Incluido como referencia del
camino a producción, con la MISMA interfaz que LocalLLMProvider. En producción,
`interpretar` y `explicar_match` harían prompting a Claude vía Bedrock, con
instrucciones de responder SOLO con base en el perfil (RNF-15, anti-alucinación).
"""

from __future__ import annotations

from app.providers.llm_base import LLMProvider, IntencionConsulta

_DEFAULT_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"


class BedrockLLMProvider(LLMProvider):
    def __init__(self, model_id: str = _DEFAULT_MODEL_ID, region: str = "us-east-1"):
        self._model_id = model_id
        self._region = region
        self._client = None

    def _ensure_client(self):  # pragma: no cover
        if self._client is None:
            try:
                import boto3  # noqa: F401
            except ImportError as exc:
                raise RuntimeError(
                    "BedrockLLMProvider requiere 'boto3' y credenciales AWS."
                ) from exc
            import boto3

            self._client = boto3.client("bedrock-runtime", region_name=self._region)
        return self._client

    def interpretar(self, consulta: str) -> IntencionConsulta:  # pragma: no cover
        # En producción: prompt a Claude pidiendo JSON estructurado (tema,
        # habilidades, nivel, dominio). Aquí no implementado (sin AWS).
        raise NotImplementedError(
            "BedrockLLMProvider.interpretar requiere entorno AWS configurado."
        )

    def explicar_match(self, consulta: str, resumen_persona: str,
                       habilidades_coincidentes: list[str]) -> str:  # pragma: no cover
        raise NotImplementedError(
            "BedrockLLMProvider.explicar_match requiere entorno AWS configurado."
        )

    @property
    def nombre(self) -> str:
        return f"bedrock:{self._model_id}"
