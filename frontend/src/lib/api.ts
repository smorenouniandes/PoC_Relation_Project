// Cliente de la API del backend.
import type { BuscarResponse } from "./types";

// En el navegador usamos la URL pública del backend; configurable por entorno.
const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function buscar(
  consulta: string,
  topK = 5
): Promise<BuscarResponse> {
  const res = await fetch(`${API_BASE}/buscar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ consulta, top_k: topK }),
  });
  if (!res.ok) {
    throw new Error(`Error del servidor (${res.status})`);
  }
  return res.json();
}

export async function enviarFeedback(
  consulta: string,
  personaId: string,
  util: boolean
): Promise<void> {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ consulta, persona_id: personaId, util }),
  });
  if (!res.ok) {
    throw new Error(`No se pudo registrar el feedback (${res.status})`);
  }
}
