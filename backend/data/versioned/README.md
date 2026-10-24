# Base de conocimiento — datasets FIJOS y versionados

Esta carpeta contiene la **base de conocimiento congelada** del PoC. Es la
**fuente de verdad** que consume la API en runtime: no se regenera ni se
recalculan embeddings al arrancar.

## Estructura

```
data/versioned/
└── <version>/                      # p. ej. v1
    ├── personas.json               # personas + fuentes + expertise (datos SINTÉTICOS)
    ├── perfiles_unificados.json    # PEU + embeddings (384 dims, modelo MiniLM)
    └── MANIFEST.json               # gobierno: procedencia, conteos, hashes SHA-256
```

## Gobierno de datos

- **Procedencia y reproducibilidad:** el `MANIFEST.json` registra cómo se generó
  el dataset (`scripts/generate_data.py` + `scripts/ingest.py`), con `num_personas`
  y `seed` deterministas, y el modelo/dimensión de embeddings.
- **Integridad:** el manifiesto guarda el `sha256` y tamaño de cada archivo.
  Verifica con: `python scripts/verify_dataset.py`.
- **Naturaleza de los datos:** `SINTETICOS` (no contienen PII real).
- **Versión activa:** controlada por la variable de entorno `DATA_VERSION`
  (por defecto `v1`). El runtime lee `data/versioned/${DATA_VERSION}/`.

## Cómo crear una nueva versión congelada

```bash
cd backend
# 1) Regenerar de forma reproducible en el área efímera
python scripts/generate_data.py --num 50 --seed 42
python scripts/ingest.py

# 2) Promover a una versión nueva (p. ej. v2)
mkdir -p data/versioned/v2
cp data/raw/personas.json data/versioned/v2/personas.json
cp data/processed/perfiles_unificados.json data/versioned/v2/perfiles_unificados.json

# 3) Generar el manifiesto de gobierno (hashes + estadísticas)
python scripts/build_manifest.py --version v2 --num 50 --seed 42

# 4) Verificar y versionar en git
python scripts/verify_dataset.py            # con DATA_VERSION=v2
git add data/versioned/v2
```

> La carpeta versionada **sí** se versiona en git (excepción explícita en
> `.gitignore`). Las carpetas `data/raw/` y `data/processed/` son de trabajo
> efímero y **no** se versionan.
