"""Consolidación de fuentes en el Perfil de Expertise Unificado (PEU).

Toma una Persona con sus fuentes y expertise y produce:
  - un `resumen` textual consolidado (base del embedding), y
  - la lista de `habilidades_clave`.

En el PoC la consolidación es basada en reglas/plantillas. En producción, un
LLM en Bedrock podría enriquecer este resumen (ver docs/04-arquitectura.md §3).
La interfaz del PEU no cambia entre ambos enfoques.

Referencia: docs/03-modelo-de-datos.md §2 y §5.
"""

from __future__ import annotations

from app.models.entities import (
    Persona,
    PerfilExpertiseUnificado,
    NivelEvidencia,
    TipoFuente,
)


# Peso de cada tipo de fuente al construir el resumen (señal de confianza).
# Las fuentes que demuestran trabajo real pesan más.
_ORDEN_FUENTES = [
    TipoFuente.CARGO,
    TipoFuente.PROYECTO,
    TipoFuente.CV,
    TipoFuente.DESCRIPCION,
]


def _habilidades_ordenadas(persona: Persona) -> list[str]:
    """Habilidades únicas, priorizando las demostradas en proyecto."""
    demostradas: list[str] = []
    autodeclaradas: list[str] = []
    vistas: set[str] = set()
    for e in persona.expertise:
        if e.habilidad in vistas:
            continue
        vistas.add(e.habilidad)
        if e.nivel_evidencia == NivelEvidencia.PROYECTO:
            demostradas.append(e.habilidad)
        else:
            autodeclaradas.append(e.habilidad)
    return demostradas + autodeclaradas


def consolidar_resumen(persona: Persona) -> str:
    """Construye el texto consolidado del perfil (base del embedding).

    Se redacta en lenguaje natural para que el embedding capture bien la
    semántica (mejor que una lista de palabras sueltas).
    """
    partes: list[str] = []
    partes.append(
        f"{persona.nombre} es {persona.cargo} ({persona.nivel.value}) "
        f"del área de {persona.area}, ubicado en {persona.ubicacion}."
    )

    habilidades = _habilidades_ordenadas(persona)
    if habilidades:
        partes.append("Habilidades y temas: " + ", ".join(habilidades) + ".")

    # Añadir el contenido de las fuentes en orden de relevancia.
    fuentes_por_tipo: dict[TipoFuente, list[str]] = {}
    for f in persona.fuentes:
        fuentes_por_tipo.setdefault(f.tipo, []).append(f.contenido_texto)

    for tipo in _ORDEN_FUENTES:
        for texto in fuentes_por_tipo.get(tipo, []):
            partes.append(texto)

    return " ".join(partes)


def construir_perfil_unificado(
    persona: Persona, embedding: list[float] | None = None
) -> PerfilExpertiseUnificado:
    """Crea el PEU de una persona (con embedding opcional ya calculado)."""
    resumen = consolidar_resumen(persona)
    habilidades_clave = _habilidades_ordenadas(persona)
    return PerfilExpertiseUnificado(
        persona_id=persona.id,
        resumen=resumen,
        habilidades_clave=habilidades_clave,
        embedding=embedding,
    )
