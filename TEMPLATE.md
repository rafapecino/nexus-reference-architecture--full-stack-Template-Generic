# Guía de uso de la plantilla BaseUE

Esta plantilla proporciona la arquitectura base para nuevos proyectos. Sigue estos pasos para adaptarla.

---

## Checklist de arranque

### 1. Clonar y renombrar

```bash
git clone <repo-url> my-new-project
cd my-new-project
```

Renombra las referencias al proyecto en estos archivos:

| Archivo | Campo | Valor a cambiar |
|---|---|---|
| `pyproject.toml` | `name` | `"baseue-template"` → `"my-project"` |
| `pyproject.toml` | `description` | Describe tu proyecto |
| `.env` / `.env.example` | `APP_LOG_NAMESPACE` | `your_project_name` → `my_project` |
| `.env` / `.env.example` | `APP_LOG_NAMESPACE_FILE` | Igual |
| `docker-compose.yml` | `container_name` | `baseue_api` / `baseue_worker` → tus nombres |
| `01_src/api/main.py` | `title`, `description` | Nombre y descripción de tu API |

### 2. Variables de entorno

```bash
cp .env.example .env
# Rellenar POSTGRES_*, STAGING_POSTGRES_*, AZURE_STORAGE_*, OPENAI_API_KEY, etc.
```

### 3. Levantar infraestructura local

```bash
docker compose up db azurite -d
```

### 4. Crear modelos de dominio

Los modelos van en `01_src/packages/data/src/data/models/`.

Los modelos conservados como referencia son:
- [item.py](01_src/packages/data/src/data/models/item.py) — modelo CRUD básico
- [audit_conversation.py](01_src/packages/data/src/data/models/audit_conversation.py) — trazabilidad de conversaciones
- [audit_event.py](01_src/packages/data/src/data/models/audit_event.py) — eventos de auditoría
- [process_instance.py](01_src/packages/data/src/data/models/process_instance.py) — seguimiento de procesos
- [mixins.py](01_src/packages/data/src/data/models/mixins.py) — mixins reutilizables

Para añadir un modelo nuevo:
1. Crear el archivo en `models/` con tu clase SQLAlchemy
2. Exportarlo en `models/__init__.py`
3. Para modelos de la BD secundaria: crear en `models/xchg/` y exportar en `models/xchg/__init__.py`

### 5. Generar migraciones

```bash
cd 01_src/packages/data

# BD principal
../../../.venv/Scripts/python.exe -m alembic revision --autogenerate -m "init domain models"
../../../.venv/Scripts/python.exe -m alembic upgrade head

# BD secundaria
../../../.venv/Scripts/python.exe -m alembic -c alembic_secondary.ini revision --autogenerate -m "init secondary models"
../../../.venv/Scripts/python.exe -m alembic -c alembic_secondary.ini upgrade head
```

> Si hay tipos `pgvector` en la migración generada, añadir manualmente: `import pgvector.sqlalchemy`

### 6. Añadir endpoints

Estructura de la API:

```
01_src/api/
├─ application/services/    Lógica de negocio
├─ domain/                  Entidades e interfaces de dominio
├─ infrastructure/          Implementaciones (repositorios, BD)
└─ interfaces/
   ├─ routers/              Endpoints FastAPI
   └─ middleware/           Middlewares
```

Para añadir un nuevo endpoint:
1. Crear `routers/my_entity.py` con el router
2. Exportarlo en `routers/__init__.py`
3. Registrarlo en `main.py` con `app.include_router(...)`

### 7. Prompts LLM

Añadir prompts en `02_artifacts/prompts/<feature>/`:

```
02_artifacts/prompts/
└─ my_feature/
   ├─ v1.0.0.md       Prompt principal
   └─ CHANGELOG.md    Historial de versiones del prompt
```

Los prompts se cargan con el `PromptLoader` de `common.prompts`.

### 8. Seed de datos

Adaptar `03_data/seed_example.py` para poblar tu base de datos en local/dev.

### 9. Tests

Los tests van en `07_tests/unit/`. Patrón recomendado:

```python
# 07_tests/unit/api/test_my_entity.py
# Mini-app con solo el router necesario (ver test_messages.py como referencia)
```

Ejecutar:
```bash
.venv/Scripts/python.exe -m pytest -m unit -v
```

---

## Convenciones del monorepo

- **DDD**: cada capa (domain, application, infrastructure, interfaces) tiene responsabilidades claras
- **Type-first**: definir tipos Pydantic antes de implementar lógica
- **Dual-DB**: BD primaria para estado interno de la app; BD secundaria para datos externos/lago
- **Workers**: cada worker es un paquete independiente que consume mensajes de cola o eventos
- **Packages**: la lógica compartida va en `packages/` (data, contracts, common, ai)

---

## Estructura de un worker nuevo

```
01_src/worker-my-worker/
├─ src/worker/
│  ├─ application/handlers/   Manejadores de mensajes
│  ├─ domain/                 Payloads y modelos de dominio
│  ├─ infrastructure/         Servicios e integraciones
│  └─ interfaces/triggers/    Disparadores (event, queue, timer)
├─ main.py
├─ runner.py
├─ pyproject.toml
└─ Dockerfile
```

Copiar `01_src/worker-xxx/` como punto de partida.
