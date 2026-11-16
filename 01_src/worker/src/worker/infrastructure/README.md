## infrastructure

Adaptadores concretos para el worker: repositorios sobre Postgres, clientes de colas, storage, LLMs o vector stores.

Convenciones:
- Implementar aqui las interfaces definidas en `application/` o `domain/`.
- Encapsular SDKs y detalles de proveedor; no incluir logica de negocio.
- Los triggers (queue/timer/event) pertenecen a infraestructura; invocan casos de uso del `application/`.
