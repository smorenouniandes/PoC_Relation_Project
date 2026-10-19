"""Router de metadatos: salud, habilidades y estadísticas."""

from __future__ import annotations

from collections import Counter

from fastapi import APIRouter, Depends

from app.api.schemas import SaludOut, HabilidadOut, EstadisticasOut
from app.api.state import AppState, get_state
from app.data_generation import catalogs as cat

router = APIRouter(tags=["meta"])


@router.get("/salud", response_model=SaludOut)
def salud(state: AppState = Depends(get_state)) -> SaludOut:
    """Health check con información básica del backend."""
    return SaludOut(
        estado="ok",
        personas_cargadas=len(state.personas),
        perfiles_cargados=len(state.perfiles),
        proveedor_embeddings=state.embedding_provider.nombre,
        proveedor_llm=state.llm_provider.nombre,
    )


@router.get("/habilidades", response_model=list[HabilidadOut])
def listar_habilidades() -> list[HabilidadOut]:
    """Catálogo de habilidades conocidas (para autocompletar en el frontend)."""
    salida: list[HabilidadOut] = []
    for categoria, lista in cat.HABILIDADES.items():
        for h in lista:
            salida.append(HabilidadOut(habilidad=h, categoria=categoria))
    return salida


@router.get("/estadisticas", response_model=EstadisticasOut)
def estadisticas(state: AppState = Depends(get_state)) -> EstadisticasOut:
    """Agregados de la población (para dashboards futuros)."""
    por_cargo = Counter(p.cargo for p in state.personas)
    por_nivel = Counter(p.nivel.value for p in state.personas)
    por_disp = Counter(p.disponibilidad.value for p in state.personas)
    habilidades = {e.habilidad for p in state.personas for e in p.expertise}
    return EstadisticasOut(
        total_personas=len(state.personas),
        por_cargo=dict(por_cargo),
        por_nivel=dict(por_nivel),
        por_disponibilidad=dict(por_disp),
        total_habilidades_unicas=len(habilidades),
    )
