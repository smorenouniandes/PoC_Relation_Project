"""Proveedor LLM LOCAL para el PoC (basado en reglas/plantillas).

No usa un modelo generativo: implementa la interfaz LLMProvider con lógica
determinista suficiente para el PoC. La búsqueda semántica (embeddings) es la
que aporta la "inteligencia"; este proveedor aporta interpretación ligera y
explicaciones legibles y verificables (sin alucinar — RNF-15).

En producción se sustituye por BedrockLLMProvider (Claude).
"""

from __future__ import annotations

import unicodedata

from app.providers.llm_base import LLMProvider, IntencionConsulta
from app.data_generation import catalogs as cat


def _normalizar(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# Vocabulario conocido a partir de los catálogos (habilidades y dominios).
_TODAS_HABILIDADES: list[str] = [
    h for lista in cat.HABILIDADES.values() for h in lista
]
_DOMINIOS: list[str] = cat.HABILIDADES["Dominio de negocio"]
_NIVELES = ["junior", "semi-senior", "semi senior", "senior", "lider", "líder"]


class LocalLLMProvider(LLMProvider):
    def interpretar(self, consulta: str) -> IntencionConsulta:
        norm = _normalizar(consulta)

        # dict.fromkeys preserva orden y elimina duplicados.
        habilidades = list(dict.fromkeys(
            h for h in _TODAS_HABILIDADES if _normalizar(h) in norm
        ))
        dominio = list(dict.fromkeys(
            d for d in _DOMINIOS if _normalizar(d) in norm
        ))

        nivel = None
        for n in _NIVELES:
            if _normalizar(n) in norm:
                nivel = n.replace("lider", "Líder").title()
                break

        # Heurística de ambigüedad: consulta corta y SIN señales específicas.
        # Palabras genéricas que no aportan foco por sí solas.
        _GENERICAS = {
            "ayuda", "necesito", "tema", "algo", "cosa", "datos", "sistema",
            "proyecto", "problema", "consulta", "informacion", "saber", "quien",
            "experto", "experta", "persona", "sobre", "para", "con",
        }
        palabras = [p for p in norm.split() if len(p) > 2]
        significativas = [p for p in palabras if p not in _GENERICAS]
        # Ambigua si no hay habilidades/dominios detectados y pocas palabras
        # significativas (foco insuficiente para buscar).
        es_ambigua = (
            not habilidades
            and not dominio
            and len(significativas) < 2
        )

        return IntencionConsulta(
            texto_original=consulta,
            habilidades=habilidades,
            nivel=nivel,
            dominio=dominio,
            es_ambigua=es_ambigua,
            aclaracion_sugerida=(
                "¿Podrías dar más detalle? Por ejemplo, la tecnología, el tema "
                "o el área de negocio en la que necesitas ayuda."
                if es_ambigua else None
            ),
        )

    def explicar_match(self, consulta: str, resumen_persona: str,
                       habilidades_coincidentes: list[str]) -> str:
        if habilidades_coincidentes:
            lista = ", ".join(habilidades_coincidentes)
            return (
                f"Coincide en {lista}, con experiencia registrada en su perfil."
            )
        # Sin coincidencia exacta de términos: el match es por afinidad semántica.
        return (
            "Su perfil es semánticamente afín a tu consulta según su experiencia "
            "y proyectos registrados."
        )

    @property
    def nombre(self) -> str:
        return "local:rule-based"
