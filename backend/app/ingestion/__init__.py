"""Pipeline de ingesta (Paso 2): fuentes -> Perfil de Expertise Unificado."""

from app.ingestion.consolidate import construir_perfil_unificado, consolidar_resumen

__all__ = ["construir_perfil_unificado", "consolidar_resumen"]
