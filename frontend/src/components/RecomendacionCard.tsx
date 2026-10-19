"use client";

import { useState } from "react";
import type { Recomendacion } from "@/lib/types";
import { enviarFeedback } from "@/lib/api";

interface Props {
  rec: Recomendacion;
  consulta: string;
}

function construirMailto(rec: Recomendacion, consulta: string): string {
  const p = rec.persona;
  const asunto = encodeURIComponent(
    `Consulta sobre: ${consulta.slice(0, 60)}`
  );
  const cuerpo = encodeURIComponent(
    `Hola ${p.nombre.split(" ")[0]},\n\n` +
      `Te contacto a través de Relation Project porque encajas con una ` +
      `necesidad que tengo:\n\n"${consulta}"\n\n` +
      `Vi que tienes experiencia en ${
        rec.habilidades_coincidentes.join(", ") || p.cargo
      }. ¿Tendrías un momento para ayudarme?\n\nGracias.`
  );
  return `mailto:${p.correo_corporativo}?subject=${asunto}&body=${cuerpo}`;
}

export default function RecomendacionCard({ rec, consulta }: Props) {
  const [voto, setVoto] = useState<boolean | null>(null);
  const [enviado, setEnviado] = useState(false);
  const p = rec.persona;

  async function votar(util: boolean) {
    setVoto(util);
    try {
      await enviarFeedback(consulta, p.id, util);
      setEnviado(true);
    } catch {
      // En el PoC, fallo silencioso de feedback no bloquea la UX.
      setEnviado(true);
    }
  }

  return (
    <article className="card">
      <div className="card-head">
        <div>
          <p className="card-name">{p.nombre}</p>
          <p className="card-role">
            {p.cargo} · {p.nivel} · {p.ubicacion}
          </p>
        </div>
        <span className={`badge ${rec.nivel_confianza}`}>
          Confianza: {rec.nivel_confianza}
        </span>
      </div>

      <p className="card-why">{rec.explicacion}</p>

      {rec.habilidades_coincidentes.length > 0 && (
        <div className="skills">
          {rec.habilidades_coincidentes.map((h) => (
            <span key={h} className="skill">
              {h}
            </span>
          ))}
        </div>
      )}

      <div className="card-actions">
        <a className="contact" href={construirMailto(rec, consulta)}>
          ✉️ Contactar
        </a>
        <span className="availability">
          <span className={`dot ${p.disponibilidad}`} />
          {p.disponibilidad}
        </span>

        {enviado ? (
          <span className="fb-thanks">¡Gracias por tu feedback!</span>
        ) : (
          <div className="feedback">
            <button
              className={`fb-btn ${voto === true ? "active" : ""}`}
              onClick={() => votar(true)}
              aria-label="Útil"
            >
              👍
            </button>
            <button
              className={`fb-btn ${voto === false ? "active" : ""}`}
              onClick={() => votar(false)}
              aria-label="No útil"
            >
              👎
            </button>
          </div>
        )}
      </div>
    </article>
  );
}
