# contracts
Contratos compartidos (Pydantic) para API, colas y eventos.

## Convenciones
- Todos los envelopes y DTOs compartidos viven aqui. Prohibido duplicar contratos en `apps/*`.
- Versionar contratos cuando cambien los campos; mantener compatibilidad hacia atras cuando sea posible.
- Productores (API/scripts/otros servicios) y consumidores (workers/API) importan desde `contracts`, no crean modelos locales.

## Contenido relevante
- `worker_message.py`: envelope estandar de mensajes de worker (process_id, process_type, step, payload, correlation_id, retry, created_at).
