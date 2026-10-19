"""Router de feedback de recomendaciones (RF-17)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import FeedbackRequest, FeedbackResponse
from app.api.state import AppState, get_state

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
def registrar_feedback(
    req: FeedbackRequest, state: AppState = Depends(get_state)
) -> FeedbackResponse:
    """Registra si una recomendación fue útil o no."""
    if state.persona(req.persona_id) is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    fid = state.registrar_feedback(
        req.consulta, req.persona_id, req.util, req.comentario
    )
    return FeedbackResponse(registrado=True, id=fid)
