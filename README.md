# PoC_Relation_Project

Iniciativa de relacionamiento diseñada para conectar personas según sus
habilidades, proyectos y experiencia, en función de necesidades específicas.

Aplicación conversacional (chat) donde describes, en lenguaje natural, un tema o
necesidad técnica, y el sistema recomienda a las **personas más indicadas** para
ayudarte, explicando **por qué** y facilitando el **contacto**.

## 🚀 Despliegue con un solo comando

```bash
docker compose up --build
```

Esto levanta todos los servicios. El backend prepara automáticamente los datos
sintéticos y los embeddings en el primer arranque (la primera vez descarga el
modelo de embeddings, puede tardar unos minutos).

| Servicio | URL |
|---|---|
| API (backend) | http://localhost:8000 |
| Documentación de la API | http://localhost:8000/docs |
| Frontend (desde el Paso 5) | http://localhost:3000 |

> **Nota:** el frontend se incorpora en el Paso 5. Hasta entonces, el backend es
> plenamente funcional por sí solo (prueba `http://localhost:8000/docs`).

## 📚 Documentación

- Ideación y diseño: carpeta [`docs/`](./docs/) (ver [índice](./docs/00-indice.md)).
- Backend (Python / FastAPI): [`backend/README.md`](./backend/README.md).

## 🧱 Enfoque

PoC ejecutable localmente con implementaciones ligeras, pero con una **capa de
abstracción** (proveedores de embeddings/LLM, repositorio de datos) que permite
migrar a producción en **AWS** (Amazon Bedrock, RDS + pgvector, S3) cambiando
solo la configuración, sin reescribir la lógica.

## 🛠️ Stack

- **Backend:** Python 3.11, FastAPI, sentence-transformers (embeddings locales).
- **Frontend:** React / Next.js (Paso 5).
- **Contenedores:** Docker + Docker Compose.
- **Producción (objetivo):** AWS — Bedrock, RDS (pgvector), S3.

## 🧩 Pasos de construcción

1. ✅ Datos sintéticos
2. ✅ Ingesta → Perfil de Expertise Unificado + embeddings
3. ✅ Motor de matching
4. ✅ API FastAPI + dockerización
5. ⏳ Frontend React/Next
