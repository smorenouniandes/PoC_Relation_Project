# 02 — Requerimientos

Este documento define **qué** debe hacer el sistema (funcionales) y **cómo** debe comportarse (no funcionales). Dado que es un banco, los requerimientos no funcionales de seguridad y privacidad tienen prioridad alta desde el PoC.

---

## A. Requerimientos Funcionales (RF)

### Consulta y conversación
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-01 | El usuario puede escribir una necesidad en lenguaje natural (español) en una interfaz de chat. | Must |
| RF-02 | El sistema interpreta la intención de la consulta (tema, tecnologías, nivel de experiencia, dominio). | Must |
| RF-03 | El sistema permite conversación de seguimiento (refinar la consulta: "¿y alguien que además sepa de AWS?"). | Should |
| RF-04 | El sistema maneja consultas ambiguas pidiendo aclaración. | Should |

### Matching y resultados
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-05 | El sistema devuelve una lista **ranqueada** de personas recomendadas (configurable, p. ej. top 3–5). | Must |
| RF-06 | Cada recomendación incluye una **explicación legible** de por qué la persona es buen match. | Must |
| RF-07 | Cada recomendación muestra un **nivel de confianza** (alto/medio/bajo) y la fuente que lo respalda. | Should |
| RF-08 | El sistema evita recomendar siempre a las mismas personas (diversidad / balanceo). | Could |
| RF-09 | Si no hay match razonable, el sistema lo informa claramente (sin inventar resultados). | Must |

### Contacto
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-10 | Cada recomendación muestra los **datos de contacto** de la persona (correo corporativo / canal). | Must |
| RF-11 | El sistema ofrece un botón para iniciar el contacto con un mensaje pre-redactado y contextualizado. | Should |
| RF-12 | 💡 El experto puede marcar su **disponibilidad** (disponible / ocupado) para ser recomendado. | Could (Fase 2) |

### Perfiles y datos
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-13 | El sistema ingiere perfiles desde múltiples fuentes (CV, perfil de cargo, descripción personal, proyectos). | Must |
| RF-14 | El sistema consolida las fuentes en un **Perfil de Expertise Unificado** por persona. | Must |
| RF-15 | El sistema considera la **recencia** de la información (un CV viejo pesa menos). | Should |
| RF-16 | 💡 La persona puede controlar qué parte de su perfil es visible y hacer opt-in/opt-out. | Could (Fase 2) |

### Aprendizaje y analítica
| ID | Requerimiento | Prioridad |
|---|---|---|
| RF-17 | El usuario puede dar feedback sobre la utilidad de una recomendación ("útil / no útil"). | Should |
| RF-18 | El sistema registra consultas sin resultado como posibles **brechas de conocimiento**. | Could |
| RF-19 | El sistema provee analítica básica de uso (consultas frecuentes, expertos más recomendados). | Could |

---

## B. Requerimientos No Funcionales (RNF)

### 🔒 Seguridad y privacidad (crítico — sector bancario)
| ID | Requerimiento | Nota |
|---|---|---|
| RNF-01 | Todos los datos sensibles (CVs, PII) deben permanecer dentro del perímetro AWS de la organización. | Motiva el uso de **Amazon Bedrock** (el modelo no envía datos a terceros). |
| RNF-02 | Cifrado de datos en reposo (S3, RDS) y en tránsito (TLS). | Estándar banca. |
| RNF-03 | Control de acceso basado en roles (quién puede consultar, quién administra). | |
| RNF-04 | Trazabilidad/auditoría: registrar quién consultó qué y cuándo. | Requisito de auditoría. |
| RNF-05 | Minimización de datos: solo se procesa lo necesario para el matching. | Principio Habeas Data (Ley 1581/2012). |
| RNF-06 | Cumplimiento de protección de datos personales y políticas internas del banco. | 🔲 Validar con área legal/seguridad. |
| RNF-07 | Datos especialmente sensibles (correo/tickets) quedan **fuera del PoC**; su inclusión requiere anonimización y aprobación. | |

### ⚡ Rendimiento y escalabilidad
| ID | Requerimiento | Meta |
|---|---|---|
| RNF-08 | Latencia de respuesta a una consulta. | < 5 s (objetivo), aceptable < 8 s en PoC. |
| RNF-09 | Escalar de ~500 (PoC) a decenas de miles de perfiles (producción) sin rediseño mayor. | Arquitectura desacoplada. |
| RNF-10 | La ingesta de perfiles es un proceso batch que no afecta la disponibilidad del chat. | |

### 🧩 Mantenibilidad y calidad
| ID | Requerimiento |
|---|---|
| RNF-11 | Desacoplar fuentes de datos del motor de matching (cambiar fuentes sin rehacer el motor). |
| RNF-12 | Código y documentación versionados en este repositorio. |
| RNF-13 | Infraestructura reproducible (preferiblemente como código — IaC). |
| RNF-14 | Observabilidad: logs, métricas y trazas del pipeline de IA. |

### 🎯 Calidad de la IA
| ID | Requerimiento |
|---|---|
| RNF-15 | El sistema **no debe alucinar** personas ni habilidades: toda afirmación se respalda en datos del perfil (RAG con citas). |
| RNF-16 | Las explicaciones deben ser verificables contra la fuente. |
| RNF-17 | Evaluación de calidad del matching con un conjunto de consultas de prueba. |

### 🌐 Usabilidad
| ID | Requerimiento |
|---|---|
| RNF-18 | Interfaz en español, clara y conversacional. |
| RNF-19 | Accesible desde navegador (web app). |
| RNF-20 | Respuestas con formato legible (listas, explicaciones, acciones de contacto). |

---

## C. Decisiones pendientes de requerimientos

- 🔲 **RNF-06:** Validar requisitos legales/seguridad específicos del banco (clasificación de datos, retención, consentimiento).
- 🔲 **RF-05:** Definir cuántos resultados mostrar por defecto (sugerido: 3–5).
- 🔲 **Roles:** ¿Quiénes son los usuarios autorizados en el PoC? (¿todo Ingeniería, o un grupo piloto?)
- 🔲 **Feedback:** ¿El feedback es obligatorio, opcional, o se infiere del comportamiento?
