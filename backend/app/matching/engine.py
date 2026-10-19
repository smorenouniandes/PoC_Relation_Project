"""Motor de matching.

Flujo (docs/04-arquitectura.md §2):
  1. Interpretación de la consulta (LLM provider).
  2. Recuperación: embedding de la consulta + similitud contra perfiles.
  3. Re-ranking: combina similitud + nivel de evidencia + recencia + diversidad.
  4. Explicación + nivel de confianza por umbrales del score final.

El ranking combinado fue acordado así:
  score = w_sem * similitud
        + w_evi * señal_evidencia
        + w_rec * señal_recencia
Luego se aplica una penalización de diversidad para no concentrar siempre a
los mismos perfiles (RF-08).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime

from app.models.entities import Persona, PerfilExpertiseUnificado, NivelEvidencia
from app.providers.base import EmbeddingProvider
from app.providers.llm_base import LLMProvider, IntencionConsulta


# --------------------------------------------------------------------------- #
# Enfoque de ranking: HÍBRIDO léxico + semántico.
#
# Hallazgo del PoC: el modelo de embeddings multilingüe compacto NO discrimina
# bien la relevancia por sí solo (consultas irrelevantes pueden dar cosenos
# altos). Por eso la RELEVANCIA se ancla en coincidencia léxica de habilidades/
# dominios (señal fuerte y verificable), y el semántico afina el orden.
#
#   score = w_lex * señal_léxica        (coincidencia de habilidades/dominio)
#         + w_sem * similitud_semántica
#         + w_evi * señal_evidencia     (demostrado en proyecto vs. autodeclarado)
#         + w_rec * señal_recencia
# --------------------------------------------------------------------------- #
W_LEXICA = 0.50
W_SEMANTICA = 0.30
W_EVIDENCIA = 0.12
W_RECENCIA = 0.08

# Umbrales de nivel de confianza sobre el score final (0..1).
UMBRAL_ALTO = 0.55
UMBRAL_MEDIO = 0.35

# Gate de relevancia: un candidato se considera SOLO si tiene coincidencia
# léxica (habilidad/dominio) O una similitud semántica razonablemente alta.
# Evita "inventar" matches cuando nadie es relevante (RF-09).
UMBRAL_SEMANTICO_SOLO = 0.33  # semántica mínima si NO hay coincidencia léxica

# Umbral final: no se muestran recomendaciones por debajo de este score
# (descarta residuales irrelevantes que sí pasaron el gate semántico).
UMBRAL_FINAL_MINIMO = 0.30

# Penalización de diversidad (resta por habilidades ya "cubiertas" por otros).
FACTOR_DIVERSIDAD = 0.05


@dataclass
class Recomendacion:
    persona: Persona
    score: float
    nivel_confianza: str              # "Alto" | "Medio" | "Bajo"
    explicacion: str
    habilidades_coincidentes: list[str] = field(default_factory=list)
    detalle_score: dict = field(default_factory=dict)


def _similitud_coseno(a: list[float], b: list[float]) -> float:
    # Los embeddings locales vienen normalizados -> producto punto ≈ coseno.
    return sum(x * y for x, y in zip(a, b))


def _senal_evidencia(persona: Persona, habilidades_consulta: list[str]) -> tuple[float, list[str]]:
    """Bonus por habilidades relevantes demostradas en proyecto vs. autodeclaradas.

    Devuelve (señal 0..1, lista de habilidades coincidentes).
    """
    if not persona.expertise:
        return 0.0, []

    consulta_norm = {h.lower() for h in habilidades_consulta}
    coincidentes: list[str] = []
    puntos = 0.0
    for e in persona.expertise:
        if e.habilidad.lower() in consulta_norm:
            coincidentes.append(e.habilidad)
            puntos += 1.0 if e.nivel_evidencia == NivelEvidencia.PROYECTO else 0.5

    if not coincidentes:
        return 0.0, []
    # Normaliza: saturar en ~3 coincidencias fuertes.
    senal = min(1.0, puntos / 3.0)
    return senal, coincidentes


def _senal_recencia(persona: Persona, hoy: datetime) -> float:
    """Señal 0..1: más reciente la actualización del perfil, mayor la señal.

    Decae suavemente: ~1.0 si es de hoy, ~0.5 a los ~2 años.
    """
    dias = max(0, (hoy - persona.fecha_actualizacion).days)
    return math.exp(-dias / 730.0)  # vida media ≈ 2 años


def _senal_lexica(perfil: PerfilExpertiseUnificado,
                  terminos_consulta: list[str]) -> tuple[float, list[str]]:
    """Fracción de términos de la consulta (habilidades/dominios) presentes en el perfil.

    Es la señal de relevancia principal: si la consulta menciona "PostgreSQL"
    y el perfil la tiene, es un match real y verificable. Devuelve
    (señal 0..1, lista de términos coincidentes).
    """
    if not terminos_consulta:
        return 0.0, []

    habilidades_perfil = {h.lower() for h in perfil.habilidades_clave}
    coincidentes = [
        t for t in terminos_consulta if t.lower() in habilidades_perfil
    ]
    if not coincidentes:
        return 0.0, []
    senal = len(coincidentes) / len(terminos_consulta)
    return senal, coincidentes


class MatchingEngine:
    def __init__(
        self,
        personas: list[Persona],
        perfiles: list[PerfilExpertiseUnificado],
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider,
    ):
        self._personas = {p.id: p for p in personas}
        self._perfiles = perfiles
        self._emb = embedding_provider
        self._llm = llm_provider

    def buscar(self, consulta: str, top_k: int = 5,
               candidatos: int = 20) -> tuple[IntencionConsulta, list[Recomendacion]]:
        """Devuelve (intención interpretada, recomendaciones ranqueadas)."""
        intencion = self._llm.interpretar(consulta)

        # Si es ambigua, no inventamos resultados (RF-04 / RF-09).
        if intencion.es_ambigua:
            return intencion, []

        hoy = datetime.utcnow()
        q_vec = self._emb.embed_one(consulta)

        # Términos de la consulta para la señal léxica (habilidades + dominios).
        terminos = list(dict.fromkeys(intencion.habilidades + intencion.dominio))

        # --- Recuperación + scoring híbrido (léxico + semántico) ---
        scored: list[tuple[PerfilExpertiseUnificado, float, float, list[str], dict]] = []
        for perfil in self._perfiles:
            if not perfil.embedding:
                continue
            persona = self._personas.get(perfil.persona_id)
            if persona is None or not persona.visible:
                continue

            sim = _similitud_coseno(q_vec, perfil.embedding)
            s_lex, coincidentes_lex = _senal_lexica(perfil, terminos)

            # GATE de relevancia (RF-09): se descarta si no hay coincidencia
            # léxica Y la semántica no es suficientemente alta por sí sola.
            if s_lex == 0.0 and sim < UMBRAL_SEMANTICO_SOLO:
                continue

            s_evi, coincidentes_evi = _senal_evidencia(persona, terminos)
            s_rec = _senal_recencia(persona, hoy)
            # Habilidades coincidentes (unión de léxicas y con evidencia).
            coincidentes = list(dict.fromkeys(coincidentes_lex + coincidentes_evi))

            score = (
                W_LEXICA * s_lex
                + W_SEMANTICA * sim
                + W_EVIDENCIA * s_evi
                + W_RECENCIA * s_rec
            )
            detalle = {
                "lexica": round(s_lex, 4),
                "similitud": round(sim, 4),
                "evidencia": round(s_evi, 4),
                "recencia": round(s_rec, 4),
            }
            scored.append((perfil, sim, score, coincidentes, detalle))

        # Orden base por score
        scored.sort(key=lambda x: x[2], reverse=True)
        scored = scored[:candidatos]

        # --- Re-ranking con diversidad ---
        recomendaciones: list[Recomendacion] = []
        habilidades_vistas: set[str] = set()

        # --- Diversidad: penaliza perfiles que repiten habilidades ya cubiertas ---
        for perfil, sim, score, coincidentes, detalle in scored:
            persona = self._personas[perfil.persona_id]
            repetidas = sum(
                1 for h in perfil.habilidades_clave[:5] if h in habilidades_vistas
            )
            score_final = max(0.0, score - FACTOR_DIVERSIDAD * repetidas)
            detalle["penalizacion_diversidad"] = round(FACTOR_DIVERSIDAD * repetidas, 4)
            detalle["score_final"] = round(score_final, 4)

            # Descartar residuales irrelevantes (RF-09).
            if score_final < UMBRAL_FINAL_MINIMO:
                continue

            nivel = (
                "Alto" if score_final >= UMBRAL_ALTO
                else "Medio" if score_final >= UMBRAL_MEDIO
                else "Bajo"
            )
            explicacion = self._llm.explicar_match(
                consulta, perfil.resumen, coincidentes
            )
            recomendaciones.append(
                Recomendacion(
                    persona=persona,
                    score=round(score_final, 4),
                    nivel_confianza=nivel,
                    explicacion=explicacion,
                    habilidades_coincidentes=coincidentes,
                    detalle_score=detalle,
                )
            )
            for h in perfil.habilidades_clave[:5]:
                habilidades_vistas.add(h)

        recomendaciones.sort(key=lambda r: r.score, reverse=True)
        return intencion, recomendaciones[:top_k]
