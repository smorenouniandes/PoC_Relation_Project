"use client";

import { useState } from "react";
import { buscar } from "@/lib/api";
import type { BuscarResponse } from "@/lib/types";
import RecomendacionCard from "@/components/RecomendacionCard";

const EJEMPLOS = [
  "Optimización de rendimiento de PostgreSQL para reportería",
  "Detección de fraude con Kafka y machine learning",
  "Riesgo de crédito y modelos de scoring",
  "Migración de microservicios a AWS",
];

export default function Home() {
  const [consulta, setConsulta] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<BuscarResponse | null>(null);
  // La consulta efectivamente buscada (para feedback y mailto).
  const [consultaBuscada, setConsultaBuscada] = useState("");

  async function ejecutar(texto: string) {
    const q = texto.trim();
    if (!q || cargando) return;
    setCargando(true);
    setError(null);
    setResultado(null);
    try {
      const data = await buscar(q);
      setResultado(data);
      setConsultaBuscada(q);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "No se pudo conectar con el servidor."
      );
    } finally {
      setCargando(false);
    }
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    ejecutar(consulta);
  }

  return (
    <main className="app">
      <header className="header">
        <h1>¿A quién necesitas para tu reto?</h1>
        <p>
          Describe tu necesidad en lenguaje natural y encuentra a las personas
          más indicadas para ayudarte.
        </p>
      </header>

      <form onSubmit={onSubmit}>
        <div className="search-box">
          <textarea
            rows={2}
            placeholder="Ej: necesito ayuda para optimizar consultas lentas en PostgreSQL…"
            value={consulta}
            onChange={(e) => setConsulta(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                ejecutar(consulta);
              }
            }}
          />
          <button className="btn" type="submit" disabled={cargando}>
            {cargando ? "Buscando…" : "Buscar"}
          </button>
        </div>
      </form>

      <p className="hint">Enter para buscar · Shift+Enter para nueva línea</p>

      {!resultado && !cargando && (
        <div className="examples">
          {EJEMPLOS.map((ej) => (
            <button
              key={ej}
              className="chip"
              onClick={() => {
                setConsulta(ej);
                ejecutar(ej);
              }}
            >
              {ej}
            </button>
          ))}
        </div>
      )}

      {cargando && <p className="loading">Analizando perfiles…</p>}

      {error && <div className="error">⚠️ {error}</div>}

      {resultado && (
        <section className="results">
          {resultado.mensaje && (
            <div className="notice">{resultado.mensaje}</div>
          )}
          {resultado.recomendaciones.map((rec) => (
            <RecomendacionCard
              key={rec.persona.id}
              rec={rec}
              consulta={consultaBuscada}
            />
          ))}
        </section>
      )}
    </main>
  );
}
