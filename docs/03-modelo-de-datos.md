# 03 — Modelo de Datos

> La calidad de las recomendaciones depende **directamente** de la calidad y riqueza de los datos de cada persona. Este es el componente más determinante del proyecto.

---

## 1. Fuentes de datos (inputs)

| Fuente | Formato típico | Naturaleza | Fase |
|---|---|---|---|
| **CV / Hoja de vida** | PDF, Word | Texto semiestructurado, heterogéneo | PoC |
| **Perfil de cargo** | Estructurado (rol, área, nivel) | Datos corporativos consistentes | PoC |
| **Descripción personal** | Texto libre | Lo que la persona dice de sí misma, intereses | PoC |
| **Proyectos** | Estructurado + texto | Proyectos en los que ha trabajado, rol, tecnologías | PoC |
| **Tickets** | Estructurado (sistema de tickets) | Evidencia de trabajo real resolviendo temas | 🔜 Fase 2 (sensible) |
| **Correo** | Texto | Alta sensibilidad, requiere anonimización | 🔜 Fase 2 (sensible) |

> ⚠️ **Nota de calidad:** Las fuentes son **heterogéneas**. Un CV en PDF, un perfil de cargo estructurado y una descripción en texto libre no se pueden comparar directamente. La **normalización y consolidación** es donde está el mayor esfuerzo real del proyecto.

> 💡 **Señal de confianza por fuente:** no todas las fuentes valen lo mismo. Un skill demostrado en un **proyecto real** o **ticket resuelto** es más fuerte que uno **auto-declarado** en el CV. El modelo de datos debe conservar el **origen** de cada señal de expertise.

---

## 2. Concepto central: Perfil de Expertise Unificado (PEU)

En vez de buscar directamente sobre fuentes crudas, consolidamos todo en un **Perfil de Expertise Unificado** por persona. Esto:

- **Desacopla** las fuentes (que cambiarán) del motor de matching (RNF-11).
- Permite comparar personas de forma homogénea.
- Es la unidad sobre la que generamos **embeddings** para la búsqueda semántica.

```
   CV ──────────┐
   Cargo ───────┤
   Proyectos ───┼──►  [ Extracción + Normalización + Consolidación ]  ──►  PERFIL DE EXPERTISE UNIFICADO
   Descripción ─┤                                                            │
   Tickets* ────┘                                                            ├─► Texto consolidado  ──► Embedding (vector)
   Correo*                                                                   └─► Metadatos estructurados (filtros)
   (*Fase 2)
```

---

## 3. Entidades del modelo

### 3.1 `Persona`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único interno |
| `nombre` | string | Nombre completo |
| `correo_corporativo` | string | Contacto (dato de contacto — RF-10) |
| `area` | string | Área (en el PoC: Ingeniería) |
| `cargo` | string | Perfil/cargo actual |
| `nivel` | enum | Junior / Semi / Senior / Líder, etc. |
| `ubicacion` | string | Ciudad / sede (opcional) |
| `disponibilidad` | enum | Disponible / Ocupado (💡 Fase 2) |
| `visible` | bool | Opt-in para ser recomendado (💡 Fase 2) |
| `fecha_actualizacion` | datetime | Para calcular recencia (RF-15) |

### 3.2 `FuenteDato`
Representa un documento/origen crudo asociado a una persona.
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | |
| `persona_id` | UUID (FK) | A quién pertenece |
| `tipo` | enum | CV / CARGO / DESCRIPCION / PROYECTO / TICKET / CORREO |
| `uri_original` | string | Ubicación del original (p. ej. S3) |
| `contenido_texto` | text | Texto extraído |
| `fecha` | datetime | Fecha del documento (para recencia) |

### 3.3 `Expertise` (señal de habilidad)
Unidad atómica de conocimiento, con su evidencia.
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | |
| `persona_id` | UUID (FK) | |
| `habilidad` | string | P. ej. "PostgreSQL", "Kafka", "AWS Lambda", "Riesgo de crédito" |
| `categoria` | string | Tecnología / Dominio de negocio / Metodología / Herramienta |
| `nivel_evidencia` | enum | AUTODECLARADO / PROYECTO / TICKET | → alimenta el nivel de confianza (RF-07) |
| `fuente_id` | UUID (FK) | De qué fuente salió |
| `recencia` | datetime | Qué tan reciente es la evidencia |

### 3.4 `PerfilExpertiseUnificado` (PEU)
| Campo | Tipo | Descripción |
|---|---|---|
| `persona_id` | UUID (FK) | |
| `resumen` | text | Texto consolidado y normalizado (base del embedding) |
| `embedding` | vector | Representación semántica (pgvector) |
| `habilidades_clave` | string[] | Para filtros rápidos |
| `fecha_generacion` | datetime | Cuándo se generó/actualizó el PEU |

### 3.5 `Consulta`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | |
| `usuario_id` | UUID | Quién consultó (trazabilidad — RNF-04) |
| `texto` | text | Consulta original en lenguaje natural |
| `intencion_extraida` | json | Tema, skills, nivel, dominio interpretados |
| `fecha` | datetime | |
| `sin_resultado` | bool | Marca brechas de conocimiento (RF-18) |

### 3.6 `Recomendacion`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | |
| `consulta_id` | UUID (FK) | |
| `persona_id` | UUID (FK) | Persona recomendada |
| `score` | float | Puntaje de relevancia |
| `nivel_confianza` | enum | Alto / Medio / Bajo |
| `explicacion` | text | Justificación legible (RF-06) |
| `feedback_util` | bool? | Feedback del usuario (RF-17) |

---

## 4. Modelo relacional (vista simplificada)

```
Persona 1───* FuenteDato
Persona 1───* Expertise *───1 FuenteDato
Persona 1───1 PerfilExpertiseUnificado
Consulta 1───* Recomendacion *───1 Persona
```

---

## 5. Pipeline de datos (alto nivel)

```
1. INGESTA        → Cargar CVs, cargos, descripciones, proyectos (batch).
2. EXTRACCIÓN     → Extraer texto (Textract para PDFs), parsear estructurados.
3. NORMALIZACIÓN  → Limpiar, unificar nomenclatura de skills (ej. "Postgres" = "PostgreSQL").
4. ENRIQUECIMIENTO→ LLM identifica habilidades, categorías y nivel de evidencia.
5. CONSOLIDACIÓN  → Generar el Perfil de Expertise Unificado por persona.
6. VECTORIZACIÓN  → Generar embeddings y almacenarlos (pgvector).
```

> ⚠️ Este pipeline es **batch** (se corre periódicamente), no en tiempo real, y no debe afectar la disponibilidad del chat (RNF-10).

---

## 6. Datos para el PoC

> 🔲 **DECISIÓN PENDIENTE — crítica:** ¿Con qué datos arrancamos el PoC?
>
> **Opción A — Datos reales (anonimizados o con consentimiento):** mayor realismo, pero requiere aprobación de seguridad/legal y acceso real a los ~500 perfiles.
>
> **Opción B — Datos sintéticos realistas:** generamos ~500 perfiles ficticios de ingenieros de banca (con CVs, cargos, proyectos verosímiles). Permite avanzar **ya** sin bloqueos legales y sirve para demostrar el flujo completo.
>
> **Recomendación:** empezar con **Opción B (sintéticos)** para construir y validar el pipeline, y migrar a datos reales cuando esté la aprobación. Esto respeta el "no ser conformistas" (construimos lo real) sin bloquearnos por el acceso a datos.

---

## 7. Decisiones pendientes de datos

- 🔲 Datos reales vs. sintéticos para el PoC (ver sección 6).
- 🔲 Taxonomía de habilidades: ¿usamos una taxonomía existente (ESCO, O*NET) o la dejamos emerger de los datos?
- 🔲 Política de recencia: ¿a partir de cuántos años un dato "pesa menos" o se descarta?
- 🔲 Nomenclatura de niveles (Junior/Senior/etc.) — alinear con la del banco.
