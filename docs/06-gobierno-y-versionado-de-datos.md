# 06 — Gobierno y Versionado de la Base de Conocimiento

> La base de conocimiento del PoC es **FIJA, versionada y reproducible**. El
> runtime la consume tal cual (no regenera datos ni recalcula embeddings al
> arrancar), lo que da arranques rápidos, resultados deterministas y
> trazabilidad para gobierno de datos.

---

## 1. Decisión

✅ **DECIDIDO:** congelar el dataset del PoC como fuente de verdad versionada en
git, en lugar de generarlo en cada arranque.

**Motivación:**
- **Determinismo:** la demo devuelve siempre los mismos resultados.
- **Gobierno:** procedencia, conteos y huellas (hashes) auditables.
- **Velocidad:** el arranque no regenera ~500 perfiles ni recalcula embeddings.
- **Reproducibilidad:** cualquiera puede re-crear el dataset bit a bit con la semilla.

---

## 2. Estructura y fuente de verdad

```
backend/data/
├── versioned/                      # ✅ VERSIONADO en git (fuente de verdad)
│   ├── README.md
│   └── v1/
│       ├── personas.json           # personas + fuentes + expertise (SINTÉTICO)
│       ├── perfiles_unificados.json# PEU + embeddings (384 dims)
│       └── MANIFEST.json           # gobierno: procedencia + hashes + estadísticas
├── raw/                            # ❌ EFÍMERO (regeneración, no versionado)
└── processed/                      # ❌ EFÍMERO (regeneración, no versionado)
```

El runtime lee la versión activa `data/versioned/${DATA_VERSION}/` (por defecto
`v1`). Solo si esa versión no existe, cae al modo de regeneración en `raw/` +
`processed/` (respaldo para experimentación local).

---

## 3. El MANIFEST.json (gobierno)

Cada versión incluye un manifiesto con:

| Campo | Para qué sirve |
|---|---|
| `dataset`, `version` | Identidad y versión del conjunto |
| `naturaleza_datos` | `SINTETICOS` — deja explícito que **no hay PII real** |
| `reproducibilidad` | `generador`, `ingesta`, `num_personas`, `seed`, `determinista` |
| `embeddings` | Modelo (`paraphrase-multilingual-MiniLM-L12-v2`), dimensión (384), normalizados |
| `archivos.*.sha256` | Huella de integridad de cada archivo |
| `estadisticas` | Conteos y distribuciones (nivel, cargo, disponibilidad, evidencia) |

> **Nota de embeddings:** se usa el **mismo modelo** para indexar los perfiles y
> para vectorizar la consulta en runtime, de modo que ambos viven en el mismo
> espacio vectorial.

---

## 4. Ciclo de vida (crear / verificar / promover una versión)

```bash
cd backend

# Regenerar de forma reproducible (área efímera)
python scripts/generate_data.py --num 50 --seed 42
python scripts/ingest.py

# Promover a una versión congelada
mkdir -p data/versioned/v2
cp data/raw/personas.json             data/versioned/v2/personas.json
cp data/processed/perfiles_unificados.json data/versioned/v2/perfiles_unificados.json

# Generar manifiesto (hashes + estadísticas) y verificar integridad
python scripts/build_manifest.py --version v2 --num 50 --seed 42
DATA_VERSION=v2 python scripts/verify_dataset.py

# Versionar
git add data/versioned/v2
```

La **versión activa** se selecciona con `DATA_VERSION` (entorno). Promover un
cambio = crear `vN+1`, no editar `vN` (inmutabilidad de versiones).

---

## 5. Integridad en el arranque

El `entrypoint.sh` ejecuta `scripts/verify_dataset.py` antes de levantar la API:
recalcula los `sha256` y los compara contra el `MANIFEST.json`. Si hay deriva
(alguien editó el dataset "congelado"), lo advierte en el log. Así el gobierno
de datos es **verificable y automatizado**, no solo documental.

---

## 6. Camino a producción

En AWS, esta base fija se reemplaza por datos reales gobernados en **RDS +
pgvector**, con S3 para documentos originales. El manifiesto (procedencia +
hashes + versión) sigue siendo válido como patrón de **data lineage** y control
de versiones de datasets, independientemente del motor de almacenamiento.
