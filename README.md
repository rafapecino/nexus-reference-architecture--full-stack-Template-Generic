# BaseUE — Monorepo Starter

Plantilla de monorepo para proyectos Python con FastAPI, dual-database PostgreSQL, workers asíncronos y soporte LangGraph/AI.

## Stack

| Capa | Tecnología |
|---|---|
| API | FastAPI + Uvicorn |
| Base de datos | PostgreSQL 16 + pgvector (dual-DB) |
| Blob Storage | Azure Blob Storage / Azurite (dev) |
| Workers | Python workers (DDD) |
| AI / Agentes | LangGraph |
| ORM / Migraciones | SQLAlchemy + Alembic (x2) |
| Gestión de paquetes | uv (workspace monorepo) |
| Calidad de código | Ruff + Black (pre-commit) |
| Tests | pytest |
| Python | 3.12.10 |

## Estructura

```
01_src/
├─ api/                   FastAPI (DDD: domain, application, infrastructure, interfaces)
├─ front/                 Frontend (vacío — añadir app aquí)
├─ worker/                Worker base (DDD)
├─ worker-xxx/            Worker adicional de ejemplo
└─ packages/
   ├─ data/               SQLAlchemy + Alembic (dual-DB: primary + secondary)
   ├─ contracts/          DTOs Pydantic (mensajería entre servicios)
   ├─ common/             Auth, config, logging, storage, embeddings
   └─ ai/                 LangGraph skeleton
02_artifacts/
└─ prompts/               Prompts LLM (vacío — añadir prompts aquí)
03_data/
├─ source_documents/      Documentos fuente (vacío)
├─ evaluation/            Artefactos de evaluación (vacío)
└─ seed_example.py        Ejemplo de seed con modelo Item
07_tests/                 Tests globales (pytest)
```

## Setup rápido

### 1. Requisitos previos
- Python 3.12.10
- [uv](https://docs.astral.sh/uv/)
- Docker Desktop

### 2. Entorno Python

```bash
uv venv .venv --python 3.12.10
uv sync --package data --package common --package contracts
```

### 3. Variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 4. Levantar infraestructura

```bash
docker compose up db azurite -d
```

### 5. Migraciones

```bash
# Base de datos principal
cd 01_src/packages/data
../../../.venv/Scripts/python.exe -m alembic upgrade head

# Base de datos secundaria (lake/staging)
../../../.venv/Scripts/python.exe -m alembic -c alembic_secondary.ini upgrade head
```

### 6. API en desarrollo

```bash
cd 01_src/api
../../../.venv/Scripts/python.exe -m uvicorn main:app --reload
# Swagger UI: http://localhost:8000/docs
```

## Tests

```bash
.venv/Scripts/python.exe -m pytest -m unit -v
```

## Patrón dual-database

La plantilla incluye soporte para dos bases de datos independientes:

- **Primary** (`POSTGRES_*`): base de datos de trabajo, borradores, estado interno
- **Secondary** (`STAGING_POSTGRES_*`): base de datos de datos lago / origen externo

Cada una tiene su propio Alembic (`alembic.ini` / `alembic_secondary.ini`) y sus propias migraciones (`migrations/` / `migrations_secondary/`).

## Personalización

Ver [TEMPLATE.md](TEMPLATE.md) para la guía completa de cómo adaptar esta plantilla a un nuevo proyecto.
