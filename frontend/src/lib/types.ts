// Tipos compartidos: reflejan los schemas de la API (backend/app/api/schemas.py).

export interface PersonaResumen {
  id: string;
  nombre: string;
  cargo: string;
  nivel: string;
  area: string;
  ubicacion: string;
  correo_corporativo: string;
  disponibilidad: string;
}

export interface Recomendacion {
  persona: PersonaResumen;
  score: number;
  nivel_confianza: "Alto" | "Medio" | "Bajo";
  explicacion: string;
  habilidades_coincidentes: string[];
  detalle_score: Record<string, number>;
}

export interface Intencion {
  texto_original: string;
  habilidades: string[];
  nivel: string | null;
  dominio: string[];
  es_ambigua: boolean;
  aclaracion_sugerida: string | null;
}

export interface BuscarResponse {
  consulta: string;
  intencion: Intencion;
  total: number;
  recomendaciones: Recomendacion[];
  mensaje: string | null;
}
