# data
Componentes de datos: ORM, entidades, repos, migraciones

## Features
- PostgreSQL database (via Docker) con Alembic para migraciones
- uv para gestion rapida de dependencias
- Variables de entorno cargadas con .env y python-dotenv
- Base service pattern para CRUD limpio

## Requisitos
- Python 3.12+ (opcional, para ejecucion local sin Docker)

## Uso de sesiones y repos base
- `data.database.session_scope()`: context manager para scripts/workers. Maneja commit/rollback y cierre.
- `data.database.get_db()`: dependency para FastAPI.
- `data.repositories.BaseRepository`: CRUD minimo (`get`, `list`, `add`, `delete`, `get_or_create`) para evitar boilerplate.
- Carga las variables de entorno (por ejemplo, con `load_dotenv()` en la app o inyectando env vars) antes de importar `data.database`, que ya no carga `.env` automaticamente.
