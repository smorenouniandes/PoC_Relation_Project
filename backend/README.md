# Backend — PoC Relation Project

Backend en Python de la PoC de relacionamiento de personas por expertise.

## Enfoque PoC vs. Producción

Este es un **PoC ejecutable localmente**. Usa implementaciones ligeras (archivos JSON, embeddings locales) pero mantiene una **capa de abstracción** para que migrar a los servicios de producción (Amazon Bedrock, RDS + pgvector, S3) sea solo cambiar el proveedor vía configuración.

| Capa | PoC (local, ejecutable aquí) | Producción (AWS) |
|---|---|---|
| LLM | Mock / reglas simples | Amazon Bedrock (Claude) |
| Embeddings | `sentence-transformers` local | Bedrock Titan Embeddings |
| Datos estructurados | Archivos JSON | Amazon RDS (PostgreSQL) |
| Base vectorial | Índice en memoria/archivo | pgvector / OpenSearch |
| Documentos originales | Carpeta local | Amazon S3 |

## Estructura

```
backend/
├── app/
│   ├── core/            # Configuración
│   ├── models/          # Entidades (dataclasses/pydantic)
│   ├── data_generation/ # Generador de datos sintéticos (Paso 1)
│   ├── ingestion/       # Pipeline de consolidación (Paso 2)
│   ├── matching/        # Motor de matching (Paso 3)
│   └── providers/       # Capa de abstracción LLM/Embeddings
├── data/
│   ├── raw/             # Datos sintéticos generados
│   └── processed/       # Perfiles unificados + embeddings
├── scripts/             # Scripts ejecutables por consola
└── requirements.txt
```

## Pasos de construcción

- [x] **Paso 1** — Estructura + generación de datos sintéticos
- [x] **Paso 2** — Ingesta → Perfil de Expertise Unificado + embeddings
- [x] **Paso 3** — Motor de matching (consola)
- [ ] Paso 4 — API FastAPI
- [ ] Paso 5 — Frontend React/Next

## Uso

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Paso 1 — generar datos sintéticos
python scripts/generate_data.py --num 50

# Paso 2 — consolidar perfiles + generar embeddings
python scripts/ingest.py

# Paso 3 — buscar expertos (consulta única o modo interactivo)
python scripts/search.py "optimización de PostgreSQL para reportería"
python scripts/search.py            # modo interactivo
```

## Motor de matching (Paso 3)

Ranking **híbrido léxico + semántico**:

```
score = 0.50 * señal_léxica       (coincidencia de habilidades/dominio)
      + 0.30 * similitud_semántica (embeddings)
      + 0.12 * evidencia           (demostrado en proyecto > autodeclarado)
      + 0.08 * recencia            (perfiles recientes pesan más)
      - penalización de diversidad (evita repetir siempre a los mismos)
```

El **nivel de confianza** (Alto/Medio/Bajo) se deriva por umbrales del score
final. Un **gate de relevancia** evita "inventar" expertos cuando nadie es un
match real (p. ej. consultas fuera de dominio devuelven "sin resultados").

> **Nota del PoC:** el modelo de embeddings multilingüe compacto no discrimina
> bien la relevancia por sí solo, por eso el ranking ancla la relevancia en la
> señal léxica. En producción, con Bedrock (Titan + Claude) y una taxonomía de
> habilidades, la calidad semántica mejora sustancialmente.
