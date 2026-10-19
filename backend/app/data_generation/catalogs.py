"""Catálogos realistas para generar perfiles sintéticos de ingeniería en banca.

Todo en español. Pensado para que los perfiles generados sean verosímiles y el
matching posterior tenga señales ricas (tecnologías + dominio de negocio).
"""

# --------------------------------------------------------------------------- #
# Nombres (para construir nombres completos verosímiles)
# --------------------------------------------------------------------------- #
NOMBRES = [
    "Ana", "Carlos", "María", "Juan", "Laura", "Andrés", "Camila", "Santiago",
    "Valentina", "Diego", "Daniela", "Felipe", "Paula", "Sebastián", "Carolina",
    "Mateo", "Natalia", "David", "Juliana", "Nicolás", "Sofía", "Esteban",
    "Catalina", "Alejandro", "Isabela", "Miguel", "Gabriela", "Ricardo",
    "Mariana", "Óscar", "Lucía", "Javier", "Adriana", "Tomás", "Verónica",
]

APELLIDOS = [
    "Rodríguez", "Gómez", "Martínez", "López", "González", "Pérez", "Sánchez",
    "Ramírez", "Torres", "Díaz", "Vargas", "Castro", "Ruiz", "Álvarez", "Romero",
    "Suárez", "Rojas", "Moreno", "Muñoz", "Gutiérrez", "Ortiz", "Delgado",
    "Castañeda", "Herrera", "Jiménez", "Mendoza", "Cárdenas", "Quintero",
]

CIUDADES = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga"]

# --------------------------------------------------------------------------- #
# Cargos del área de Ingeniería
# --------------------------------------------------------------------------- #
CARGOS = [
    "Ingeniero de Software",
    "Ingeniero de Datos",
    "Arquitecto de Software",
    "Arquitecto de Datos",
    "Ingeniero DevOps",
    "Ingeniero de Seguridad",
    "Ingeniero de Machine Learning",
    "Ingeniero de Confiabilidad (SRE)",
    "Desarrollador Backend",
    "Desarrollador Frontend",
    "QA Automation Engineer",
    "Ingeniero de Plataforma Cloud",
]

# --------------------------------------------------------------------------- #
# Habilidades por categoría
# --------------------------------------------------------------------------- #
# categoria -> lista de habilidades
HABILIDADES = {
    "Lenguaje": [
        "Java", "Python", "JavaScript", "TypeScript", "Go", "C#", "Kotlin",
        "Scala", "COBOL", "SQL",
    ],
    "Tecnología": [
        "Spring Boot", "Node.js", "React", "Angular", "Kafka", "Docker",
        "Kubernetes", "PostgreSQL", "Oracle", "MongoDB", "Redis", "GraphQL",
        "gRPC", "RabbitMQ", "Elasticsearch",
    ],
    "Cloud": [
        "AWS Lambda", "Amazon S3", "Amazon RDS", "Amazon EKS", "AWS Glue",
        "Amazon SageMaker", "Terraform", "CloudFormation",
    ],
    "Metodología": [
        "Microservicios", "Arquitectura Hexagonal", "Event-Driven",
        "CI/CD", "TDD", "DDD", "Scrum", "Observabilidad",
    ],
    "Dominio de negocio": [
        "Riesgo de crédito", "Medios de pago", "Core bancario",
        "Banca digital", "Fraude transaccional", "Cumplimiento (SARLAFT)",
        "Reportería regulatoria", "Tesorería", "Cartera", "Open Banking",
    ],
    "Datos/ML": [
        "Ingeniería de datos", "Data Warehouse", "Modelos de scoring",
        "NLP", "Series de tiempo", "Pipelines de ML", "Gobierno de datos",
    ],
}

# --------------------------------------------------------------------------- #
# Plantillas de proyectos (dominio bancario)
# --------------------------------------------------------------------------- #
PROYECTOS = [
    "Migración del core bancario a microservicios",
    "Plataforma de pagos en tiempo real",
    "Modernización del datawarehouse para reportería regulatoria",
    "Motor de detección de fraude transaccional",
    "App de banca digital para personas",
    "Modelo de scoring de riesgo de crédito",
    "Integración Open Banking con terceros",
    "Automatización de cumplimiento SARLAFT",
    "Plataforma de observabilidad y monitoreo",
    "Migración de infraestructura a AWS",
    "Sistema de notificaciones transaccionales",
    "Onboarding digital de clientes",
    "API Gateway corporativo",
    "Pipeline de datos para tesorería",
]

ROLES_PROYECTO = [
    "líder técnico", "desarrollador principal", "arquitecto", "integrante del equipo",
    "responsable de datos", "encargado de pruebas", "DevOps del proyecto",
]

# --------------------------------------------------------------------------- #
# Fragmentos para descripciones personales
# --------------------------------------------------------------------------- #
DESCRIPCION_INTROS = [
    "Me apasiona",
    "Disfruto trabajar en",
    "Tengo especial interés en",
    "Me gusta profundizar en",
    "He enfocado mi carrera en",
]

DESCRIPCION_TEMAS = [
    "la construcción de sistemas distribuidos resilientes",
    "la optimización de rendimiento de bases de datos",
    "el diseño de arquitecturas limpias y mantenibles",
    "la automatización de despliegues y la cultura DevOps",
    "resolver problemas de negocio con datos",
    "la seguridad de aplicaciones en entornos regulados",
    "mentoría técnica y buenas prácticas de ingeniería",
    "la adopción de cloud en banca",
]
