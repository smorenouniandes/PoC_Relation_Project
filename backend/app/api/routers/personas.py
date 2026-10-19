"""Router de personas: listado y detalle de perfiles."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.schemas import (
    PersonaResumenOut, PersonaDetalleOut, FuenteOut, ExpertiseOut,
)
from app.api.state import AppState, get_state

router = APIRouter(prefix="/personas", tags=["personas"])


def _resumen(p) -> PersonaResumenOut:
    return PersonaResumenOut(
        id=p.id,
        nombre=p.nombre,
        cargo=p.cargo,
        nivel=p.nivel.value,
        area=p.area,
        ubicacion=p.ubicacion,
        correo_corporativo=p.correo_corporativo,
        disponibilidad=p.disponibilidad.value,
    )


@router.get("", response_model=list[PersonaResumenOut])
def listar_personas(
    state: AppState = Depends(get_state),
    cargo: str | None = Query(None, description="Filtrar por cargo"),
    disponibilidad: str | None = Query(None, description="Disponible/Ocupado"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[PersonaResumenOut]:
    """Lista personas con filtros opcionales (útil para futuras pantallas)."""
    personas = state.personas
    if cargo:
        personas = [p for p in personas if cargo.lower() in p.cargo.lower()]
    if disponibilidad:
        personas = [
            p for p in personas
            if p.disponibilidad.value.lower() == disponibilidad.lower()
        ]
    return [_resumen(p) for p in personas[offset: offset + limit]]


@router.get("/{persona_id}", response_model=PersonaDetalleOut)
def obtener_persona(
    persona_id: str, state: AppState = Depends(get_state)
) -> PersonaDetalleOut:
    """Devuelve el detalle completo de una persona (fuentes y expertise)."""
    p = state.persona(persona_id)
    if p is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    base = _resumen(p).model_dump()
    return PersonaDetalleOut(
        **base,
        visible=p.visible,
        fecha_actualizacion=p.fecha_actualizacion.isoformat(),
        fuentes=[
            FuenteOut(tipo=f.tipo.value, contenido_texto=f.contenido_texto,
                     fecha=f.fecha.isoformat())
            for f in p.fuentes
        ],
        expertise=[
            ExpertiseOut(habilidad=e.habilidad, categoria=e.categoria,
                        nivel_evidencia=e.nivel_evidencia.value)
            for e in p.expertise
        ],
    )
