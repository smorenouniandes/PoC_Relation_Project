# 01 — Visión y Alcance

## 1. El problema

En una entidad bancaria grande, el conocimiento técnico está **distribuido entre cientos de personas**, pero no existe una forma eficiente de saber **quién sabe qué**. Cuando alguien necesita ayuda con un tema específico (una tecnología, un proyecto, un dominio del negocio), encontrar a la persona adecuada depende de:

- El boca a boca y las redes informales de cada quien.
- A quién conoces personalmente (sesgo hacia los mismos nombres de siempre).
- Búsquedas manuales en directorios que no reflejan la expertise real.

Esto genera: **pérdida de tiempo, duplicación de esfuerzos, dependencia de pocas "personas estrella" y desaprovechamiento del talento existente.**

## 2. La visión

> Una aplicación conversacional donde cualquier colaborador escribe su necesidad en lenguaje natural y, en segundos, obtiene una lista explicada de las personas más indicadas para ayudarle — junto con la forma de contactarlas.

**Ejemplo de interacción:**

> **Usuario:** "Necesito ayuda para optimizar el rendimiento de una base de datos PostgreSQL que está lenta en consultas de reportería."
>
> **App:** Te recomiendo 3 personas:
> 1. **Ana Rodríguez** (Arquitecta de Datos) — Lideró la optimización del datawarehouse en 2024; su CV destaca tuning de PostgreSQL y particionamiento. _Confianza: Alta_
> 2. **Carlos Pérez** (Ingeniero Senior) — Trabajó en el proyecto de reportería regulatoria; experiencia en índices y query planning. _Confianza: Media_
> 3. ...
>
> _[Contactar a Ana] [Contactar a Carlos]_

## 3. Objetivos

### Objetivos del PoC
1. **Validar la hipótesis central:** que es posible recomendar expertos con calidad a partir de datos existentes (CVs, perfiles de cargo, proyectos, descripciones personales).
2. **Demostrar el flujo completo** de consulta → matching → explicación → contacto.
3. **Construir una base técnica sólida y escalable a producción** (sin atajos desechables).
4. **Identificar los retos reales** de calidad de datos, privacidad y rendimiento con ~500 personas de Ingeniería.

### Objetivos del producto (visión a producción)
- Reducir el tiempo de encontrar a la persona correcta.
- Democratizar el acceso al conocimiento interno (romper el sesgo de "a quién conoces").
- Visibilizar talento oculto y balancear la carga de consultas entre expertos.
- Generar inteligencia organizacional: mapa de capacidades y **brechas de conocimiento**.

## 4. Métricas de éxito del PoC

| Métrica | Meta orientativa |
|---|---|
| Precisión percibida del match (feedback "útil") | ≥ 70% de consultas con al menos 1 resultado útil |
| Cobertura | Perfiles consolidados para ≥ 90% de las ~500 personas |
| Latencia de respuesta | < 5 s por consulta (objetivo producción más estricto) |
| Explicabilidad | 100% de resultados con justificación legible |

> 🔲 **DECISIÓN PENDIENTE:** confirmar con el patrocinador del proyecto cuáles son las métricas de éxito "oficiales" para aprobar el paso a producción.

## 5. Alcance por fases

### ✅ Fase PoC (foco actual)
- Chat para consulta en lenguaje natural (frontend web real).
- Ingesta y consolidación de perfiles desde: **CVs, perfiles de cargo, descripción personal, proyectos**.
- Motor de matching semántico con explicación del resultado.
- Visualización de resultados ranqueados + **datos de contacto**.
- Población inicial: ~500 personas del área de Ingeniería.
- Registro básico de feedback y trazabilidad de consultas.

### 🔜 Fase 2 (post-PoC, hacia producción)
- Integración con fuentes adicionales: **tickets, correo** (con gobierno de datos y anonimización).
- Autenticación corporativa (SSO).
- Panel de administración y gestión de perfiles.
- Señal de disponibilidad del experto y control de privacidad (opt-in).
- Feedback loop que reentrena/ajusta el ranking.

### 🔮 Fase 3 (visión)
- Expansión a toda la organización (no solo Ingeniería).
- Analítica de brechas de conocimiento para RRHH/liderazgo.
- Notificaciones y gestión de solicitudes de conexión dentro de la app.
- Recomendación proactiva (sugerir expertos según proyectos en curso).

## 6. Fuera de alcance (del PoC)

- ❌ Integración con correo y tickets (se evalúa para Fase 2).
- ❌ Sistema de mensajería interno (el contacto se hace por canales existentes: correo/Teams/etc.).
- ❌ Gestión de desempeño o evaluación de personas (esto **no** es una herramienta de evaluación).
- ❌ Expansión fuera del área de Ingeniería.

## 7. Supuestos y riesgos iniciales

| Tipo | Descripción |
|---|---|
| ⚠️ Supuesto | Se dispondrá de acceso a CVs, perfiles de cargo, descripciones y datos de proyectos de las ~500 personas. |
| ⚠️ Riesgo | Calidad y heterogeneidad de los datos (CVs en formatos distintos, información desactualizada). |
| ⚠️ Riesgo | Privacidad y cumplimiento (datos personales en sector bancario regulado). |
| ⚠️ Riesgo | Aceptación cultural: que las personas acepten ser recomendadas y contactadas. |
| ⚠️ Supuesto | Uso de AWS (incl. Amazon Bedrock) está aprobado para procesar estos datos. |

## 8. Principios de diseño

1. **Explicable antes que mágico** — cada recomendación debe justificarse.
2. **Privacidad por diseño** — minimización de datos y control del individuo.
3. **Escalable desde el día 1** — el PoC no es código desechable.
4. **La calidad del dato manda** — invertir en normalización/consolidación.
5. **Humano al centro** — la app sugiere; la persona decide.
