# 05 — Casos de Uso y Flujos

Este documento ilustra **cómo se usa** la aplicación con ejemplos concretos. Sirve para alinear expectativas y, más adelante, como base de los casos de prueba de calidad del matching (RNF-17).

---

## 1. Actores

| Actor | Descripción |
|---|---|
| **Consultante** | Colaborador de Ingeniería que busca ayuda sobre un tema. Usuario principal del PoC. |
| **Experto recomendado** | Persona cuyo perfil hace match. En Fase 2 puede gestionar su disponibilidad/visibilidad. |
| **Administrador** | Gestiona la ingesta de datos, monitorea el sistema. |
| 🔜 **Liderazgo / RRHH** | (Fase 3) Consume analítica de brechas de conocimiento. |

---

## 2. Caso de uso principal: Buscar un experto

**Flujo:**
1. El consultante abre el chat y describe su necesidad en lenguaje natural.
2. El sistema interpreta la intención (tema, tecnologías, nivel, dominio).
3. Si la consulta es ambigua, el sistema pide una aclaración.
4. El sistema recupera y ranquea candidatos.
5. El sistema muestra 3–5 personas con explicación, nivel de confianza y contacto.
6. El consultante elige a quién contactar (botón con mensaje pre-redactado).
7. El consultante da feedback (útil / no útil).

---

## 3. Ejemplos de consultas y respuestas esperadas

### Ejemplo 1 — Consulta técnica específica
> **Consultante:** "Tengo una base PostgreSQL lenta en consultas de reportería, ¿quién me puede ayudar con optimización?"

**Respuesta esperada:**
```
Encontré 3 personas que podrían ayudarte:

1. Ana Rodríguez · Arquitecta de Datos · Confianza: Alta
   Por qué: Lideró el proyecto de optimización del datawarehouse (2024).
   Su CV destaca tuning de PostgreSQL y particionamiento de tablas.
   📧 ana.rodriguez@banco.com   [Contactar a Ana]

2. Carlos Pérez · Ingeniero Senior · Confianza: Media
   Por qué: Participó en reportería regulatoria; experiencia en índices
   y planes de ejecución.
   📧 carlos.perez@banco.com   [Contactar a Carlos]

3. ...
```

### Ejemplo 2 — Consulta de dominio de negocio
> **Consultante:** "Necesito entender el cálculo de provisiones de riesgo de crédito para un nuevo microservicio."

**Respuesta esperada:** personas que combinen conocimiento de **dominio bancario (riesgo de crédito)** + **técnico (microservicios)**. Ilustra que el matching no es solo de tecnologías, sino también de dominio.

### Ejemplo 3 — Consulta de seguimiento (refinamiento)
> **Consultante:** "Gracias. De esos, ¿alguno tiene además experiencia con AWS?"

**Respuesta esperada:** el sistema mantiene el contexto de la conversación (RF-03) y filtra/re-ranquea los resultados previos por experiencia en AWS.

### Ejemplo 4 — Consulta ambigua
> **Consultante:** "Necesito ayuda con un tema de datos."

**Respuesta esperada:** el sistema pide aclaración (RF-04):
> "¿Podrías darme más detalle? Por ejemplo: ¿es sobre bases de datos, ingeniería de datos, analítica, gobierno de datos...?"

### Ejemplo 5 — Sin resultados
> **Consultante:** "¿Quién sabe de programación en COBOL para mainframe z/OS con integración a blockchain?"

**Respuesta esperada (RF-09):** el sistema informa que no encontró un match razonable, **no inventa personas**, y registra la consulta como posible brecha de conocimiento (RF-18).

---

## 4. Caso de uso: Dar feedback

1. Tras ver los resultados, el consultante marca una recomendación como "útil" o "no útil".
2. El sistema registra el feedback asociado a la consulta y la persona (RF-17).
3. El feedback alimenta la mejora del ranking y las métricas de éxito del PoC.

---

## 5. Caso de uso: Ingesta de perfiles (Administrador)

1. El administrador carga/actualiza las fuentes (CVs, cargos, descripciones, proyectos).
2. El pipeline batch extrae, normaliza, consolida y vectoriza los perfiles.
3. El administrador verifica cobertura (¿cuántas personas quedaron con perfil completo?).

---

## 6. Caso de uso (Fase 2): Gestión del experto

- El experto marca su **disponibilidad** (disponible / ocupado).
- El experto controla la **visibilidad** de su perfil y hace **opt-in/opt-out** de ser recomendado.
- El experto puede corregir/complementar su perfil.

---

## 7. Caso de uso (Fase 3): Analítica de brechas

- Liderazgo/RRHH consulta un panel con:
  - Consultas más frecuentes.
  - Temas sin expertos suficientes (brechas de conocimiento).
  - Expertos más recomendados (riesgo de sobrecarga / dependencia).

---

## 8. Escenarios de calidad (para pruebas)

> Estos escenarios servirán como **conjunto de evaluación** del matching (RNF-17):

| # | Tipo de consulta | Qué valida |
|---|---|---|
| 1 | Tecnología específica | Precisión en skills técnicos |
| 2 | Dominio de negocio | Matching por conocimiento de negocio |
| 3 | Combinada (tecnología + dominio) | Matching multidimensional |
| 4 | Ambigua | Manejo de aclaraciones |
| 5 | Sin resultados | No alucinar, detectar brechas |
| 6 | Seguimiento | Manejo de contexto conversacional |

> 🔲 **DECISIÓN PENDIENTE:** definir un set de ~20–30 consultas reales representativas del área de Ingeniería para medir la calidad del matching de forma objetiva.
