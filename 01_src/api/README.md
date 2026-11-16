# api
API principal (backend)

# Configuración
Instalar los paquetes comunes
    pip install -e packages/data -e packages/contracts -e packages/common

# Despliegue CI/Prod (App Service / Functiones / ACA Jobs)
Construye wheels versionados:
    pip wheel packages/data -w wheels/
En Dockerfile de cada app copia/instala: pip install wheels/data-0.1.0-py3-none-any.whl
Ventaja: despliegues reproducibles y sin dependencias de ruta.

# Migraciones
Se aplican siempre desde packages/data (job único en CI).
    En local:
        cd packages/data
        alembic upgrade head

## EjecuciИn local rбpida
1. Crear y activar entorno: `python -m venv .venv && .\\.venv\\Scripts\\activate`
2. Instalar dependencias: `pip install -r requirements.txt -e packages/data -e packages/contracts -e packages/common`
3. Levantar Postgres (desde raнz): `docker compose up -d db`
4. Aplicar migraciones: `cd packages/data && alembic upgrade head`
5. Arrancar la API: `cd apps/api && uvicorn main:app --reload --port 8000`

## Swagger y smoke tests
- Swagger: `http://127.0.0.1:8000/docs`
- Salud: `curl http://127.0.0.1:8000/health`
- Versiзn: `curl http://127.0.0.1:8000/version`
- BD: `curl http://127.0.0.1:8000/db/ping`
- CRUD rбpido de items:
  - Crear: `curl -X POST http://127.0.0.1:8000/items/ -H "Content-Type: application/json" -d '{"name":"demo","description":"prueba"}'`
  - Listar: `curl http://127.0.0.1:8000/items/`
  - Consultar: `curl http://127.0.0.1:8000/items/1`
  - Actualizar: `curl -X PUT http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d '{"description":"nueva"}'`
  - Borrar: `curl -X DELETE http://127.0.0.1:8000/items/1`
