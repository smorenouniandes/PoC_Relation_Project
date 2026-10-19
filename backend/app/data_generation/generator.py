"""Generador de personas sintéticas para el PoC.

Crea perfiles verosímiles de ingeniería en banca con sus cuatro fuentes de datos
del PoC (CV, cargo, descripción, proyectos) y las señales de Expertise derivadas,
con su nivel de evidencia. Reproducible mediante `seed`.

Referencia: docs/03-modelo-de-datos.md
"""

from __future__ import annotations

import random
import unicodedata
from datetime import datetime, timedelta

from app.data_generation import catalogs as cat
from app.models.entities import (
    Persona,
    FuenteDato,
    Expertise,
    TipoFuente,
    NivelEvidencia,
    Nivel,
    Disponibilidad,
)


def _slug(texto: str) -> str:
    """Normaliza un nombre a texto ASCII en minúsculas para el correo."""
    nfkd = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.lower().replace(" ", ".")


def _fecha_pasada(rng: random.Random, max_dias: int = 1460) -> datetime:
    """Fecha aleatoria en el pasado (hasta ~4 años) para modelar recencia."""
    return datetime.utcnow() - timedelta(days=rng.randint(0, max_dias))


def _elegir_habilidades(rng: random.Random) -> dict[str, list[str]]:
    """Selecciona un subconjunto coherente de habilidades por categoría."""
    seleccion: dict[str, list[str]] = {}
    for categoria, lista in cat.HABILIDADES.items():
        # Entre 1 y 3 habilidades por categoría (algunas categorías pueden quedar vacías)
        k = rng.randint(0, min(3, len(lista)))
        if k > 0:
            seleccion[categoria] = rng.sample(lista, k)
    # Garantizar que la persona tenga al menos algo de contenido técnico
    if not seleccion:
        cat_tec = "Tecnología"
        seleccion[cat_tec] = rng.sample(cat.HABILIDADES[cat_tec], 2)
    return seleccion


def _construir_persona(rng: random.Random, indice: int) -> Persona:
    nombre = f"{rng.choice(cat.NOMBRES)} {rng.choice(cat.APELLIDOS)}"
    # Correo único garantizado con el índice
    correo = f"{_slug(nombre)}.{indice}@banco.com"
    cargo = rng.choice(cat.CARGOS)
    nivel = rng.choices(
        list(Nivel),
        weights=[25, 30, 35, 10],  # pocos líderes, mayoría mid/senior
        k=1,
    )[0]
    disponibilidad = rng.choices(
        list(Disponibilidad), weights=[75, 25], k=1
    )[0]

    persona = Persona(
        nombre=nombre,
        correo_corporativo=correo,
        area="Ingeniería",
        cargo=cargo,
        nivel=nivel,
        ubicacion=rng.choice(cat.CIUDADES),
        disponibilidad=disponibilidad,
        fecha_actualizacion=_fecha_pasada(rng, max_dias=365),
    )

    habilidades = _elegir_habilidades(rng)
    habilidades_planas = [h for lista in habilidades.values() for h in lista]

    # ---- Fuente: Perfil de cargo (estructurado) ----
    fuente_cargo = FuenteDato(
        persona_id=persona.id,
        tipo=TipoFuente.CARGO,
        contenido_texto=(
            f"Cargo: {cargo}. Nivel: {nivel.value}. Área: Ingeniería. "
            f"Sede: {persona.ubicacion}."
        ),
        fecha=persona.fecha_actualizacion,
    )

    # ---- Fuente: CV (texto con habilidades autodeclaradas) ----
    anios_exp = {
        Nivel.JUNIOR: rng.randint(1, 3),
        Nivel.SEMI_SENIOR: rng.randint(3, 6),
        Nivel.SENIOR: rng.randint(6, 12),
        Nivel.LIDER: rng.randint(8, 18),
    }[nivel]
    fuente_cv = FuenteDato(
        persona_id=persona.id,
        tipo=TipoFuente.CV,
        contenido_texto=(
            f"{nombre} — {cargo} con {anios_exp} años de experiencia. "
            f"Competencias: {', '.join(habilidades_planas)}."
        ),
        fecha=_fecha_pasada(rng, max_dias=1460),
    )

    # ---- Fuente: Descripción personal (texto libre) ----
    descripcion = (
        f"{rng.choice(cat.DESCRIPCION_INTROS)} {rng.choice(cat.DESCRIPCION_TEMAS)}"
        f" y {rng.choice(cat.DESCRIPCION_TEMAS)}."
    )
    fuente_desc = FuenteDato(
        persona_id=persona.id,
        tipo=TipoFuente.DESCRIPCION,
        contenido_texto=descripcion,
        fecha=persona.fecha_actualizacion,
    )

    # ---- Fuentes: Proyectos (demuestran expertise real) ----
    num_proyectos = rng.randint(1, 4)
    proyectos = rng.sample(cat.PROYECTOS, num_proyectos)
    fuentes_proyecto: list[FuenteDato] = []
    # Habilidades demostradas en proyectos: subconjunto de las que tiene
    habilidades_en_proyecto = set(
        rng.sample(habilidades_planas, min(len(habilidades_planas), rng.randint(1, 4)))
    )
    for proyecto in proyectos:
        rol = rng.choice(cat.ROLES_PROYECTO)
        tech_usada = rng.sample(
            habilidades_planas, min(len(habilidades_planas), rng.randint(1, 3))
        )
        habilidades_en_proyecto.update(tech_usada)
        fuentes_proyecto.append(
            FuenteDato(
                persona_id=persona.id,
                tipo=TipoFuente.PROYECTO,
                contenido_texto=(
                    f"Proyecto: {proyecto}. Rol: {rol}. "
                    f"Tecnologías/temas: {', '.join(tech_usada)}."
                ),
                fecha=_fecha_pasada(rng, max_dias=1460),
            )
        )

    persona.fuentes = [fuente_cargo, fuente_cv, fuente_desc, *fuentes_proyecto]

    # ---- Derivar señales de Expertise con nivel de evidencia ----
    expertise: list[Expertise] = []
    for categoria, lista in habilidades.items():
        for habilidad in lista:
            demostrada = habilidad in habilidades_en_proyecto
            expertise.append(
                Expertise(
                    persona_id=persona.id,
                    habilidad=habilidad,
                    categoria=categoria,
                    nivel_evidencia=(
                        NivelEvidencia.PROYECTO
                        if demostrada
                        else NivelEvidencia.AUTODECLARADO
                    ),
                    fuente_id=fuente_cv.id,
                    recencia=_fecha_pasada(rng, max_dias=1460),
                )
            )
    persona.expertise = expertise

    return persona


def generar_personas(num: int = 50, seed: int = 42) -> list[Persona]:
    """Genera `num` personas sintéticas de forma reproducible.

    Args:
        num: cantidad de personas a generar.
        seed: semilla para reproducibilidad.
    """
    rng = random.Random(seed)
    return [_construir_persona(rng, i) for i in range(num)]
