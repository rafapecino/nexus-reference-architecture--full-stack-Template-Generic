# Slice de referencia: Item

Este slice muestra la linea a seguir al implementar un caso de uso extremo a extremo en la maqueta. Usa `Item` como ejemplo de referencia sin invadir el dominio real.

## Recorrido rapido
- Datos: `packages/data/src/data/models/item.py`, esquemas `packages/data/src/data/schemas/item.py`, repositorio `packages/data/src/data/repositories/item.py`.
- API: router CRUD `apps/api/interfaces/routers/item.py`, servicio `apps/api/application/services/item.py`.
- Worker: payload de dominio `apps/worker/src/worker/domain/item_payload.py`, handlers de ejemplo `apps/worker/src/worker/application/handlers/item_demo.py`, registro en `apps/worker/src/worker/main.py`.
- Tests de guia: `tests/unit/worker/test_item_handlers.py` (unitarios de handlers con fakes).
- Front: deja un servicio o hook dedicado en `apps/front/src/` (p. ej. `lib/api/items.ts`) consumiendo los contratos anteriores.

## Flujo HTTP sincrono (API)
- Endpoints disponibles: `GET /items`, `POST /items`, `GET /items/{id}`, `PUT /items/{id}`, `DELETE /items/{id}`.
- El router delega en `ItemService` (capa `application`) y usa los esquemas Pydantic de `data.schemas.item`.
- `ItemRepository` ilustra un upsert idempotente por nombre; reutilizalo si necesitas acceso directo desde servicios u otros adaptadores.
- Ejemplo rapido:
  - Crear: `curl -X POST http://127.0.0.1:8000/items/ -H "Content-Type: application/json" -d '{"name":"demo","description":"prueba"}'`
  - Listar: `curl http://127.0.0.1:8000/items/`
  - Actualizar: `curl -X PUT http://127.0.0.1:8000/items/1 -H "Content-Type: application/json" -d '{"description":"nueva"}'`

## Flujo asincrono (worker demo)
- `process_type`: `item_demo`.
- Pasos:
  1) `validate_item`: valida/normaliza el payload con `ItemPayload` y agenda el siguiente paso.
  2) `persist_item`: usa `ItemRepository.upsert_by_name` para persistir de forma idempotente y devuelve el `item_id`.
- Mensaje base a procesar (cola/CLI):
```json
{"process_id":"<uuid>","process_type":"item_demo","step":"validate_item","payload":{"name":"demo","description":"opcional"},"correlation_id":"<uuid>","retry":0,"created_at":"<iso-datetime>"}
```
- Ejecucion en local (requiere BD, migraciones aplicadas y variables `POSTGRES_*`/`AZURE_STORAGE_CONNECTION_STRING`):
```
python -m worker.main --process-type item_demo --step validate_item --payload '{"name":"demo","description":"prueba"}'
```
- El orquestador registra el estado en `process_instances`. Si necesitas encadenar pasos de forma asincrona, el trigger/cola debe publicar un nuevo `WorkerMessage` con `next_step` y (opcionalmente) `next_payload`.

## Tests como contrato de uso
- `tests/unit/worker/test_item_handlers.py` muestra:
  - Validacion de payload y paso siguiente.
  - Upsert idempotente mediante un repositorio fake inyectado.
- Replica el patron para tus procesos: handlers testeables con dependencias inyectables/fakes y sin depender de BD real.
- Para la API, sigue el mismo enfoque con `TestClient` y dependencias sobreescritas (`get_db`) para aislar tests unitarios.

## Como replicarlo para otro dominio
1) Define el modelo ORM y esquemas Pydantic en `packages/data/src/data/models` y `.../schemas`; genera migracion Alembic y documentala.
2) Crea un repositorio especializado en `packages/data/src/data/repositories`.
3) Expone servicios en `apps/api/application/services` y routers en `apps/api/interfaces/routers` usando esos esquemas.
4) Si hay pipelines asincronos, crea payloads en `apps/worker/src/worker/domain` y handlers en `apps/worker/src/worker/application/handlers`, registralos en `main.py` o via import dedicado.
5) Anade tests unitarios que funcionen con fakes (sin BD real) y documenta el recorrido en `docs/`.
6) En el front, encapsula el acceso en un servicio/hooks reutilizables y apunta a los contratos compartidos.
