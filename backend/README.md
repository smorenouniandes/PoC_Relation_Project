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
- [ ] Paso 2 — Ingesta → Perfil de Expertise Unificado + embeddings
- [ ] Paso 3 — Motor de matching (consola)
- [ ] Paso 4 — API FastAPI
- [ ] Paso 5 — Frontend React/Next

## Uso (Paso 1)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_data.py --num 50
```
