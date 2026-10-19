# 04 — Arquitectura

> Enfoque: **búsqueda semántica + RAG (Retrieval-Augmented Generation)** sobre perfiles de personas, construido sobre **AWS**, con frontend web real y pensado para escalar a producción.

---

## 1. Visión general

El sistema tiene dos grandes flujos:

1. **Flujo de ingesta (batch, offline):** toma las fuentes de datos, las consolida en Perfiles de Expertise Unificados y genera embeddings.
2. **Flujo de consulta (online, tiempo real):** el usuario pregunta en el chat, el sistema recupera candidatos, los ranquea y genera explicaciones.

---

## 2. Pipeline de consulta (RAG)

```
  Usuario (chat)
       │  "Necesito ayuda con tuning de PostgreSQL en reportería"
       ▼
┌───────────────────────────────────────────────────────────────┐
│ 1. INTERPRETACIÓN DE INTENCIÓN (LLM / Bedrock)                  │
│    Extrae: tema, tecnologías, nivel, dominio de negocio         │
└───────────────────────────────────────────────────────────────┘
       │  intención estructurada + texto de consulta
       ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. RECUPERACIÓN (Retrieval)                                     │
│    - Embedding de la consulta (Bedrock Titan Embeddings)        │
│    - Búsqueda vectorial en pgvector (top-K candidatos)          │
│    - Filtros opcionales (área, nivel, disponibilidad)           │
└───────────────────────────────────────────────────────────────┘
       │  N candidatos con sus perfiles
       ▼
┌───────────────────────────────────────────────────────────────┐
│ 3. RE-RANKING                                                   │
│    Combina: similitud semántica + nivel de evidencia +          │
│    recencia + balanceo de carga (diversidad)                    │
└───────────────────────────────────────────────────────────────┘
       │  top 3–5 personas
       ▼
┌───────────────────────────────────────────────────────────────┐
│ 4. GENERACIÓN DE EXPLICACIÓN (LLM / Bedrock)                    │
│    Por cada persona: justificación legible + nivel de confianza │
│    (RAG: citando evidencia del perfil, SIN alucinar)            │
└───────────────────────────────────────────────────────────────┘
       │
       ▼
  Resultado al usuario: lista ranqueada + explicación + contacto
       │
       ▼
  [ Feedback "útil/no útil" + trazabilidad de la consulta ]
```

---

## 3. Pipeline de ingesta (batch)

```
  Fuentes (CV, cargo, descripción, proyectos)
       │
       ▼
  [ S3: almacenamiento de documentos originales ]
       │
       ▼
  [ Extracción de texto: Amazon Textract (PDFs) + parsers ]
       │
       ▼
  [ Normalización + Enriquecimiento con LLM (Bedrock) ]
       │   → identifica habilidades, categorías, nivel de evidencia
       ▼
  [ Consolidación → Perfil de Expertise Unificado ]
       │
       ├──►  [ RDS PostgreSQL: datos estructurados ]
       └──►  [ pgvector: embeddings de perfiles ]
```

---

## 4. Stack tecnológico

> ✅ **DECIDIDO:** Infraestructura AWS. Frontend web real (no Streamlit). Idioma español.

| Capa | Tecnología propuesta | Justificación |
|---|---|---|
| **Frontend** | React + Next.js + TypeScript | Web app seria y escalable; buen ecosistema para chat UI. |
| **Backend / API** | Python + FastAPI | Estándar en IA/ML, async, excelente para orquestar RAG. |
| **LLM** | **Amazon Bedrock** (p. ej. Claude) | Datos **no salen** del perímetro AWS → clave en banca (RNF-01). |
| **Embeddings** | Amazon Bedrock (Titan Embeddings) | Mismo perímetro de seguridad. |
| **Base vectorial** | **pgvector** sobre Amazon RDS (PostgreSQL) | Un solo motor para datos + vectores; simple y escalable. Alt: OpenSearch. |
| **Datos estructurados** | Amazon RDS (PostgreSQL) | Personas, expertise, consultas, feedback. |
| **Documentos originales** | Amazon S3 | CVs y archivos fuente (cifrado en reposo). |
| **Extracción de texto** | Amazon Textract | OCR/parsing de CVs en PDF. |
| **Orquestación RAG** | LangChain o LlamaIndex | Acelera el pipeline; 🔲 a evaluar cuál. |
| **Autenticación** | Amazon Cognito | Base para SSO corporativo (Fase 2). |
| **Infra como código** | Terraform o AWS CDK | Reproducibilidad (RNF-13); 🔲 a elegir. |
| **Observabilidad** | Amazon CloudWatch | Logs, métricas, trazas (RNF-14). |

---

## 5. Diagrama de componentes (AWS)

```
┌────────────┐      HTTPS      ┌──────────────────┐
│  Navegador │ ──────────────► │  Frontend (Next)  │
│  (usuario) │ ◄────────────── │   en AWS (p.ej.    │
└────────────┘                 │  Amplify/ECS/S3+CF)│
                               └─────────┬──────────┘
                                         │ API REST
                                         ▼
                               ┌──────────────────┐
                               │  Backend FastAPI  │
                               │   (ECS / Lambda)  │
                               └───┬─────────┬──────┘
                                   │         │
                 ┌─────────────────┘         └──────────────────┐
                 ▼                                               ▼
        ┌──────────────────┐                          ┌──────────────────┐
        │  Amazon Bedrock  │                          │ RDS PostgreSQL    │
        │  (LLM + Embed.)  │                          │  + pgvector       │
        └──────────────────┘                          └──────────────────┘
                                                                ▲
  INGESTA (batch)                                               │
  ┌──────────┐   ┌───────────┐   ┌──────────────────┐           │
  │   S3     │──►│ Textract  │──►│ Proceso de        │───────────┘
  │ (CVs...) │   │ (OCR)     │   │ consolidación +   │
  └──────────┘   └───────────┘   │ embeddings (Bedrock)│
                                 └──────────────────┘

  Transversal: Cognito (auth) · CloudWatch (observabilidad) · KMS (cifrado)
```

> 🔲 **DECISIÓN PENDIENTE — cómputo del backend:** ¿ECS/Fargate (servicio siempre activo, mejor para latencia baja) vs. Lambda (serverless, costo por uso)? Para un PoC con tráfico bajo, Lambda es económico; para producción con latencia estable, ECS/Fargate.

> 🔲 **DECISIÓN PENDIENTE — hosting del frontend:** AWS Amplify (más simple) vs. S3 + CloudFront vs. contenedor en ECS.

---

## 6. Decisiones técnicas clave y alternativas

| Decisión | Opción elegida | Alternativas | Estado |
|---|---|---|---|
| Proveedor de nube | AWS | — | ✅ Decidido |
| LLM | Amazon Bedrock | OpenAI/Anthropic API pública | ✅ Decidido (por privacidad) |
| Base vectorial | pgvector (RDS) | OpenSearch, Pinecone, Qdrant | 🔲 Propuesto |
| Frontend | React + Next.js | Angular, Vue | 🔲 Propuesto |
| Backend | Python + FastAPI | Node.js | 🔲 Propuesto |
| Orquestación RAG | LangChain / LlamaIndex | Implementación propia | 🔲 A evaluar |
| Cómputo backend | ECS/Fargate o Lambda | — | 🔲 Pendiente |
| IaC | Terraform o CDK | — | 🔲 Pendiente |

---

## 7. Consideraciones de escalabilidad (PoC → producción)

- **Desacoplamiento** (RNF-09, RNF-11): el motor de matching no conoce las fuentes; solo consume Perfiles Unificados. Agregar tickets/correo en Fase 2 no toca el motor.
- **Vectorial:** pgvector sirve bien hasta cientos de miles de vectores; si se supera, migrar a OpenSearch/servicio dedicado sin cambiar la lógica de aplicación (interfaz de repositorio).
- **Batch de ingesta** independiente del flujo online → escalan por separado.
- **Costos:** el mayor costo recurrente son las llamadas a Bedrock; mitigar con caché de embeddings e interpretación.

---

## 8. Seguridad en la arquitectura (resumen)

- 🔒 Todo dentro de la cuenta/VPC de AWS del banco (RNF-01).
- 🔒 Cifrado en reposo (S3, RDS) con KMS y en tránsito (TLS) (RNF-02).
- 🔒 IAM con mínimo privilegio; roles separados para ingesta vs. consulta (RNF-03).
- 🔒 Auditoría de consultas en RDS/CloudTrail (RNF-04).
- 🔒 Correo y tickets **excluidos** del PoC (RNF-07).
