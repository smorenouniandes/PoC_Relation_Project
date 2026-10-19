"""Punto de entrada de la API FastAPI del PoC Relation Project.

Expone el motor de matching vía HTTP. CORS habilitado para desarrollo local
(frontend React/Next). La inicialización de datos/motor se hace de forma
perezosa en el primer uso (ver app.api.state).
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import busqueda, feedback, personas, meta

app = FastAPI(
    title="PoC Relation Project — API",
    description=(
        "Recomendación de expertos por consulta en lenguaje natural. "
        "Documentación interactiva en /docs."
    ),
    version="0.4.0",
)

# --- CORS (desarrollo local) ---
# Orígenes permitidos configurables por entorno; por defecto, localhost.
_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(meta.router)
app.include_router(busqueda.router)
app.include_router(feedback.router)
app.include_router(personas.router)


@app.get("/", tags=["meta"])
def raiz() -> dict:
    return {
        "nombre": "PoC Relation Project — API",
        "docs": "/docs",
        "salud": "/salud",
    }
