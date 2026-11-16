# Guia base-starter de la maqueta

Esta documentacion explica como utilizar la maqueta fullstack de este repositorio como punto de partida para proyectos nuevos. Actua como manual base-starter: describe las piezas del monorepo, los flujos de trabajo recomendados y los lugares donde anadir documentacion y configuracion especifica de cada cliente o dominio.

## Objetivos
- Arrancar proyectos con una estructura coherente y lista para Docker.
- Reutilizar las capas comunes (datos, contratos, utilidades) en API, frontend y workers.
- Facilitar el onboarding del equipo con convenciones claras.
- Separar la documentacion generica de la particular de cada proyecto.

## Estructura del monorepo
- `packages/data`: Capa de datos con SQLAlchemy y Alembic. Contiene `src/data/models` y `migrations/`.
- `packages/contracts`: Modelos Pydantic compartidos (DTOs) para la API, el frontend y workers.
- `packages/common`: Utilidades comunes (auth, logging, clientes externos) pensadas para ser importadas desde API/worker.
- `packages/ai`: Esqueleto base de LangGraph (estado, tools, tracing, checkpointer en memoria) reutilizable desde API o workers.
- `apps/api`: Servicio FastAPI que consume `data` y `contracts`.
- `apps/front`: Frontend Next.js que llama a la API. Usa variables `NEXT_PUBLIC_...` para la URL base.
- `apps/worker-*`: Ejemplos de procesos asincronos o funciones programadas.
- `infra/`: IAC y pipelines de CI/CD; adaptable segun proveedor cloud.
- `docs/`: Documentacion de la maqueta y espacio para la documentacion especifica de cada proyecto.

## Convenciones generales
- Python 3.12 y Node.js LTS.
- Formato de codigo: `ruff`/`black` en Python (anadir a CI si el proyecto lo requiere) y `eslint`/`prettier` en el front.
- Dependencias backend gestionadas con `uv` + `uv.lock` unico de workspace; frontend con npm/pnpm/yarn.
- Evitar logica de negocio en los routers de FastAPI: usar servicios/clases en `apps/api/services`.
- Migraciones siempre con Alembic autogenerate + revision manual.
- Modelos ORM solo en `packages/data/src/data/models/`; contratos compartidos (HTTP/colas/eventos) solo en `packages/contracts/src/contracts/`. No duplicar en `apps/*`.
- Documenta las reglas de estilo, tipado y pruebas en `docs/coding-guidelines.md` y crea variantes por cliente en `docs/projects/<proyecto>/coding-guidelines.md`.

## Dockerizacion y 12-factor
- Imagenes base `python:3.12-slim` con multi-stage en `apps/api/Dockerfile` y `apps/worker/Dockerfile`, instalando dependencias con `uv sync --frozen --no-dev --package <service>` apoyado en `uv.lock`.
- Configuracion solo via variables de entorno: consulta `.env.example` para la lista minima y usa `.env` local (no comitear secretos) o variables inyectadas en CI/CD.
- `docker-compose.yml` incluye Postgres, Azurite, API y worker; lanza todo con `docker compose up api worker` tras definir las variables.
- No hay credenciales ni endpoints hardcodeados: si falta una variable requerida, la aplicacion falla al arrancar (12-factor).

## Flujos de trabajo recomendados
1. **Entorno local**
   - Crear y activar un entorno virtual Python (por ejemplo `uv venv .venv && .venv/Scripts/activate` en Windows).
   - Instalar dependencias con `uv sync` usando el lock: `uv sync --frozen --extra dev` (incluye herramientas de desarrollo) o `uv sync --frozen --no-dev --package api`/`--package worker` si solo quieres runtime minimo.
   - Levantar servicios base o stack completo: `docker compose up -d db azurite` o `docker compose up api worker`.
   - Para usar LangGraph en API o worker, importa desde `packages/ai` y añade tus nodos/tools al `GraphBuilder`.
   - Estructura recomendada por capas (por servicio):
     - `domain/`: reglas y modelos puros.
     - `application/`: casos de uso/servicios.
     - `infrastructure/`: adaptadores (DB, colas, LLM, vector store, triggers).
     - `interfaces/`: routers/controladores/puntos de entrada.
  - Observabilidad/auditoría: contratos y modelos base para conversación/LLM (`packages/contracts/src/contracts/audit_conversation.py`, `packages/data/src/data/models/audit_conversation.py`) y auditoría genérica de eventos (`packages/contracts/src/contracts/audit_event.py`, `packages/data/src/data/models/audit_event.py`). Servicios base en API: `apps/api/application/services/audit_conversation_service.py` (mensajes/LLM) y `apps/api/application/services/audit_event_service.py` (acciones de usuario/worker). Exportadores OTel/App Insights se activan por proyecto.
  - Observabilidad/auditoría: contratos y modelos base en `packages/contracts/src/contracts/audit_conversation.py` y `packages/data/src/data/models/audit_conversation.py`; servicio de auditoría en `apps/api/application/services/audit_conversation_service.py` listo para extender. Exportadores OTel/App Insights se activan por proyecto.
2. **Migraciones**
   - Anadir/editar modelos en `packages/data/src/data/models`.
   - Generar migracion: `cd packages/data && alembic revision --autogenerate -m "cambio"`.
   - Revisar la migracion y aplicar: `alembic upgrade head`.
3. **API**
   - Endpoints en `apps/api/interfaces/routers` (ej: `/health`, `/version`, `/messages`), logica en `apps/api/application`.
   - Usa los modelos de `contracts` para I/O y `data` para acceso a BD.
   - `/messages` expone el contrato base del runtime IA (200 sync / 202 async) y errores estandar `{code, message, trace_id, detail}`.
4. **Frontend**
   - Ejecutar `npm install` en `apps/front` y `npm run dev`.
   - Consumir la API usando la URL configurada en `.env.local` (`NEXT_PUBLIC_API_BASE_URL`).
5. **Workers**
   - Crear un worker en `apps/worker-<nombre>` compartiendo `common`, `contracts` y `data` via `-e ../../packages/...` en su `requirements.txt`.
   - Consulta `docs/architecture/worker-skeleton.md` para el diseno base, estados, reintentos y registro de pasos antes de crear un worker nuevo.
6. **Pruebas**
   - API: `pytest` desde `apps/api/tests`.
   - Front: `npm test` o `npm run lint` segun configuracion.
   - Anade validaciones de formato/seguridad a CI si el proyecto lo necesita.

### Entorno para tests (local y CI)
- Usa `.env.test` como base sin secretos reales y cРplicalo a `.env` antes de instalar deps o lanzar tests: `cp .env.test .env`.
- Instala dependencias de todo el workspace y extras de desarrollo con `uv sync --frozen --extra dev --package gestion-contenidos --package api --package worker --package common --package data --package contracts --package ai`.
- Ejecuta los unit tests principales con `uv run pytest -q -m unit` (el mismo comando que en la CI).
- Si necesitas validar todo el suite, omite el marcador: `uv run pytest -q`.


## Calidad: Ruff, Black y pre-commit
- Instala herramientas de dev (incluye Ruff, Black, pre-commit, pytest) desde la raiz con `uv pip install --system --constraint constraints.txt --requirement requirements.txt`.
- Activa hooks locales con `pre-commit install` y ejecutalos una vez con `pre-commit run --all-files`.
- Lint: `ruff check .` y, si quieres autocorregir imports/simplificaciones, `ruff check --fix .`.
- Formato: `black .` o solo validar con `black --check .`.
- CI de la maqueta ejecuta `ruff check .`, `black --check .` y `pytest -m unit` (`.github/workflows/ci-common-unit-tests.yml`). Replica estos pasos en tu pipeline si usas otro sistema.
- FastAPI: se ignora `B008` en `apps/api/interfaces/routers/**` porque `Depends(...)` en defaults es el patron recomendado; 

## Como adaptar la maqueta a un proyecto
1. **Configurar `.env` raiz** con credenciales de BD/Azure segun el entorno.
2. **Documentacion especifica**
   - Crea una carpeta `docs/projects/<proyecto>` para decisiones de dominio, requerimientos y manuales de uso.
   - Separa la arquitectura base de la variante del cliente: usa `docs/architecture` para la maqueta y `docs/architecture/<proyecto>` para decisiones o diagramas particulares.
3. **Infra y despliegue**
   - Ajusta `docker-compose.yml` si cambian los servicios base (por ejemplo, colas o caches).
   - Duplica/parametriza plantillas en `infra/pipelines` y `infra/iac` para cada entorno.
4. **Seguridad y observabilidad**
   - Anade middlewares de auth en la API dentro de `apps/api/services` o `apps/api/dependencies`.
   - Configura logging centralizado en `packages/common` y metricas/tracing segun el stack elegido.
5. **Front**
   - Define paginas/routers en `apps/front/src/app` y servicios de datos que lean de la API.
   - Documenta variantes de branding o feature flags en `docs/projects/<proyecto>/front.md`.

## Puntos de integracion clave
- **URL de base de datos** se compone con variables `POSTGRES_*` en `.env` y se usa en Alembic y FastAPI.
- **Almacenamiento**: Azurite emula Azure Storage; sustituye por Azure real en despliegue y documenta las claves en `docs/projects/<proyecto>/storage.md`.
- **Contratos**: todas las entradas/salidas publicas deben definirse en `packages/contracts` para minimizar divergencias entre API, front y workers.

## Checklist para iniciar un proyecto
- [ ] Crear repositorio derivado de esta maqueta.
- [ ] Completar `.env` y `.env.local` (front).
- [ ] Ejecutar `docker compose up -d db azurite` y `alembic upgrade head`.
- [ ] Configurar CI con lint + tests.
- [ ] Documentar decisiones de arquitectura: base en `docs/architecture` y variaciones en `docs/architecture/<proyecto>`.
- [ ] Anadir documentacion de dominio en `docs/projects/<proyecto>`.

## Proximos pasos sugeridos
- Anadir plantillas de ADR y de documentacion de endpoints en `docs/architecture`.
- Incorporar scripts de make/Invoke o tareas npm para automatizar los flujos anteriores.
- Integrar checks de calidad (lint, tests, type-checking) en CI/CD.
- Consultar `docs/mixins.md` para reutilizar mixins de modelos, API y operaciones.
