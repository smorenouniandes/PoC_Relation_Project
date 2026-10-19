"""Router de búsqueda de expertos."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas import (
    BuscarRequest, BuscarResponse, RecomendacionOut,
    PersonaResumenOut, IntencionOut,
)
from app.api.state import AppState, get_state

router = APIRouter(tags=["búsqueda"])


@router.post("/buscar", response_model=BuscarResponse)
def buscar(req: BuscarRequest, state: AppState = Depends(get_state)) -> BuscarResponse:
    """Busca las personas más indicadas para una necesidad en lenguaje natural."""
    intencion, recomendaciones = state.engine.buscar(req.consulta, top_k=req.top_k)

    intencion_out = IntencionOut(
        texto_original=intencion.texto_original,
        habilidades=intencion.habilidades,
        nivel=intencion.nivel,
        dominio=intencion.dominio,
        es_ambigua=intencion.es_ambigua,
        aclaracion_sugerida=intencion.aclaracion_sugerida,
    )

    mensaje = None
    if intencion.es_ambigua:
        mensaje = intencion.aclaracion_sugerida
    elif not recomendaciones:
        mensaje = ("No se encontraron personas con un match razonable "
                   "(registrado como posible brecha de conocimiento).")

    recs_out = [
        RecomendacionOut(
            persona=PersonaResumenOut(
                id=r.persona.id,
                nombre=r.persona.nombre,
                cargo=r.persona.cargo,
                nivel=r.persona.nivel.value,
                area=r.persona.area,
                ubicacion=r.persona.ubicacion,
                correo_corporativo=r.persona.correo_corporativo,
                disponibilidad=r.persona.disponibilidad.value,
            ),
            score=r.score,
            nivel_confianza=r.nivel_confianza,
            explicacion=r.explicacion,
            habilidades_coincidentes=r.habilidades_coincidentes,
            detalle_score=r.detalle_score,
        )
        for r in recomendaciones
    ]

    return BuscarResponse(
        consulta=req.consulta,
        intencion=intencion_out,
        total=len(recs_out),
        recomendaciones=recs_out,
        mensaje=mensaje,
    )
