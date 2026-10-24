# 📚 Documentación de Ideación — PoC Relation Project

> **Qué es este proyecto:** Una aplicación conversacional (chat) donde un colaborador describe, en lenguaje natural, un tema o necesidad técnica, y el sistema recomienda a las **personas más indicadas** para ayudarle dentro de la organización, explicando **por qué** son buen match y facilitando el **contacto**.

## Contexto

| Dimensión | Definición |
|---|---|
| **Organización** | Entidad bancaria (sector financiero regulado) |
| **Alcance PoC** | ~500 personas del área de Ingeniería con expertise técnica |
| **Objetivo final** | Arquitectura replicable a producción para toda la organización |
| **Infraestructura** | AWS |
| **Idioma** | Español |
| **Estado** | Prueba de Concepto (PoC) — sin código aún, fase de ideación |

## Índice de documentos

| # | Documento | Descripción |
|---|---|---|
| 01 | [Visión y Alcance](./01-vision-y-alcance.md) | Problema, visión, objetivos, alcance por fases, fuera de alcance |
| 02 | [Requerimientos](./02-requerimientos.md) | Requerimientos funcionales y no funcionales (seguridad, privacidad, rendimiento) |
| 03 | [Modelo de Datos](./03-modelo-de-datos.md) | Fuentes de datos, el "Perfil de Expertise Unificado", entidades |
| 04 | [Arquitectura](./04-arquitectura.md) | Stack AWS, pipeline de RAG, diagramas, decisiones técnicas |
| 05 | [Casos de Uso](./05-casos-de-uso.md) | Ejemplos de consultas, resultados esperados, flujos de usuario |
| 06 | [Gobierno y Versionado de Datos](./06-gobierno-y-versionado-de-datos.md) | Base de conocimiento fija, versionada y reproducible; manifiesto, integridad y ciclo de vida |

## Convenciones

- 🔲 **DECISIÓN PENDIENTE** — requiere validación o input para cerrarse.
- ✅ **DECIDIDO** — acordado con el equipo.
- 💡 **IDEA / MEJORA** — propuesta opcional para enriquecer el producto.
- ⚠️ **RIESGO / ALERTA** — punto que requiere atención especial (seguridad, datos, cumplimiento).

## Cómo evoluciona esta documentación

Estos documentos son **vivos**: se actualizan a medida que cerramos decisiones. El orden sugerido de lectura es secuencial (01 → 05).
