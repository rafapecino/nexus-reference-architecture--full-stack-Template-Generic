# Skeleton de Worker Generico — Template/Base

## Objetivo
Generar un esqueleto de worker generico reutilizable en distintos proyectos, no especifico de dominio, preparado para:
- ejecutarse como proceso backend desacoplado,
- reaccionar a distintos tipos de trigger,
- ejecutar procesos de uno o varios pasos,
- coordinar pasos mediante colas,
- persistir y actualizar el estado del proceso en base de datos,
- integrarse con los paquetes comunes (`common`, `data`).

Este worker NO implementa logica de negocio, solo el patron tecnico.

---

## Principios de diseño (obligatorios)
1. Stateless: sin estado en memoria entre ejecuciones; el estado persiste en BD o mensajes.
2. Idempotencia: reintentos seguros; mismo mensaje puede procesarse varias veces.
3. Observabilidad: logging estructurado con `common.logging`; correlacion por `process_id` / `correlation_id`.
4. Infra-agnostico: sin dependencias de Azure Functions, Celery, etc.; el runtime se monta encima.
5. Extensible: facil añadir procesos/pasos sin tocar el core.

## Idempotencia y concurrencia
- Clave idempotente: `(process_id, step)`. Rechazar duplicados en BD/cola.
- Optimistic locking: columna `version` en `process_instances`; reintentar si hay `StaleDataError`.
- Ningun handler debe tener efectos externos sin verificar idempotencia (marcar en BD antes de side-effects).

---

## Triggers soportados
- Queue trigger: mensaje entrante desde cola (Azure Storage Queue / Service Bus).
- Timer trigger: ejecucion periodica (cron-like).
- Event trigger: evento externo (webhook, evento de dominio, etc.).
- Manual trigger: invocado desde script o API (util para reprocesos).
El core solo recibe un `WorkerMessage`, el trigger es un wrapper.

---

## Conceptos clave
### Proceso
- Unidad logica de trabajo de alto nivel.
- Estado global persistido en BD.
- Uno o varios pasos.

### Paso
- Unidad de ejecucion concreta.
- Puede ejecutarse inline o publicar mensaje para continuar asincrono.

---

## Modelo de datos minimo (`process_instances`)
Fuente unica en `packages/data/src/data/models/process_instance.py`. Ningun modelo ORM en `apps/*`.

Campos minimos:
- `id` (UUID / PK)
- `process_type` (string)
- `status` (enum/string: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`, `DEAD_LETTER`)
- `current_step` (string | nullable)
- `input_data` (JSONB)
- `output_data` (JSONB | nullable)
- `error` (string | nullable)
- `version` (int, para locking optimista)
- `created_at`
- `updated_at`
No se define dominio, solo estructura tecnica.

## Estados y transiciones de proceso
Estados: `PENDING -> RUNNING -> COMPLETED | FAILED | CANCELLED | DEAD_LETTER`
- `RETRYING` es alias transitorio de `RUNNING` con `retry > 0`.
Reglas:
- Solo pasar a `RUNNING` si esta en `PENDING/RETRYING`.
- `CANCELLED` solo con flag de cancelacion activo.
- `DEAD_LETTER` si se supera el limite de reintentos o error no recuperable.
- `current_step` se actualiza atomicamente junto con `status` y `version`.

---

## Mensaje de cola estandar (estructura base)
Envelope comun extendible por proceso:
```json
{
  "process_id": "uuid",
  "process_type": "string",
  "step": "string",
  "payload": {},
  "correlation_id": "uuid",
  "retry": 0,
  "created_at": "iso-datetime"
}
```
Notas: `payload` libre por proceso/paso; `retry` controla reintentos; `correlation_id` para logging distribuido.

## Contrato de WorkerMessage (obligatorio)
- Se define en `packages/contracts/src/contracts/worker_message.py` (Pydantic). Prohibido duplicarlo en `apps/*`.
- Los triggers y handlers del worker importan desde `contracts.worker_message`.

Campos obligatorios:
- `process_id` (uuid)
- `process_type` (string)
- `step` (string)
- `payload` (objeto libre del proceso/paso)
- `correlation_id` (uuid)
- `retry` (int, >= 0)
- `created_at` (iso-datetime)

Validaciones minimas:
- `step` debe existir en el registro de handlers para el `process_type`.
- `retry` no puede exceder el limite configurado.
- `payload` se valida con esquema del paso (pydantic/DTO).
- Compatibilidad: versionar el mensaje si cambian campos; rechazar o mapear versiones antiguas.

---

## Estructura de carpetas sugerida
apps/
  worker/
    src/worker/
      main.py                # entrypoint generico
      runner.py              # core del worker
      handlers/
        base.py              # interfaz de paso
        registry.py          # registro de procesos/pasos
      triggers/
        base.py              # interfaz de trigger
        queue.py
        timer.py
        event.py
      services/
        process_service.py   # creacion/actualizacion estado en BD
    README.md
packages/
  contracts/
    src/contracts/worker_message.py  # contrato compartido (Pydantic)
  data/
    src/data/models/process_instance.py  # modelo SQLAlchemy base

---

## Flujo de ejecucion (alto nivel)
1. Trigger recibe evento/mensaje/timer.
2. Trigger construye un `WorkerMessage` (desde `contracts`).
3. `runner` valida, carga o crea `ProcessInstance`, marca `RUNNING`.
4. Ejecuta el handler del paso.
5. El paso devuelve resultado final o publica mensaje para siguiente paso.
6. Actualiza estado en BD: `COMPLETED` o `FAILED` (con error).
7. Logging en cada transicion.

---

## Registro de procesos y pasos
- Interfaz: `get_handler(process_type, step) -> StepHandler`.
- Validacion en arranque: fallar si falta handler declarado.
- Handlers no abren sesiones; usan servicios inyectados (`process_service`).

---

## Observabilidad
- Logging estructurado con `common.logging`; incluir siempre `process_id`, `correlation_id`, `process_type`, `step`, `status`, `retry`.
- Metricas: contadores por estado final, latencia por paso, tasa de reintentos, volumen a DLQ.
- Tracing: propagar `correlation_id`; mapear `trace_id` externo si existe.
- Sanitizar payload en logs (sin PII).

## Integracion con LangGraph (limites sanos)
- El orquestador del worker se usa para batch/ingesta/jobs multi-paso. No debe gestionar el estado conversacional ni decidir el siguiente nodo de un grafo IA.
- Para flujos IA con estado (tool-calling, retrieval, checkpoints), usar LangGraph desde `packages/ai`:
  - El grafo decide transiciones y mantiene su estado/checkpoint.
  - El worker solo envuelve la ejecucion del grafo como un paso del pipeline (si procede), controlando reintentos a nivel de job, no de nodo.
- Checkpoint del grafo: usa `MemorySaver` por defecto o un checkpointer propio (Postgres/Redis/Azure Storage) inyectado al `GraphBuilder`; no mezclarlo con la tabla `process_instances`.
- Tracing IA: emplear los hooks de LangGraph (`log_graph_event`) para tokens/tool-calls; el logging del worker queda para el job envolvente.

---

## Ingesta RAG (job) y versionado de indice
- Ejecutar la ingesta como job independiente (contenedor/entrypoint especifico) reejecutable e idempotente.
- Reutilizar `process_instances` para trazar cada run de ingesta: `process_type` (p. ej. `rag_ingest`), `status`, `error` y metadata clave.
- Versionado y trazabilidad minima en metadata del proceso:
  - `index_version`
  - `fuentes` (lista de origenes/paths)
  - `chunks_total`, `chunks_duplicados`, `chunks_descartados`
  - `started_at`, `finished_at`
- Registrar eventos de ingesta (no LLM) con `AuditEventService` (actor=worker, action=ingest, entity=index, metadata con metricas).
- El template no incluye un handler RAG por defecto; crea un handler en tu proyecto y registralo en el `registry`. Puedes invocarlo con el CLI (`python -m worker.main --process-type rag_ingest --step ingest --payload '{...}'`) o mediante triggers/colas propios.

---

## Integraciones obligatorias
- `common.logging`
- `data`:
  - `SessionLocal` / `session_scope`
  - mixins estandar (timestamps, status)
- No acceder directamente a BD sin pasar por `data`.
- Contratos:
  - `WorkerMessage` en `packages/contracts` como unica fuente de verdad.
- `packages/ai`:
  - Para grafos IA, importar estado/tools/tracing base y ejecutarlos como paso; la transicion/estado del grafo no debe vivir en el orquestador del worker.

---

## Politica de reintentos
- Backoff exponencial con jitter (configurable, placeholder).
- Persistir: `retry_count`, `last_error`, `last_attempt_at`.
- Limite de reintentos configurable; al exceder, mover a `DEAD_LETTER`.
- DLQ: registrar motivo y payload para analisis.

## Aspectos a dejar preparados (aunque no implementados)
- Dead-letter queue.
- Locks optimistas (versionado).
- Cancelacion de procesos.
- Escalado horizontal (workers multiples).

---

## Configuracion y seguridad
- Inyeccion por entorno/config: conexion BD, endpoints de cola/eventos, nivel de log, limites de retry, timeouts por paso.
- Validar payloads con esquemas (pydantic/DTO); rechazar si no cumplen.
- No loggear datos sensibles; enmascarar campos configurables.

---

## Testing recomendado
- Unitarias del runner (transiciones de estado, reintentos, DLQ).
- Unitarias de handlers con esquemas de payload.
- Integracion con `session_scope` y modelo `process_instances` (locking, reintentos).
- Contrato de `WorkerMessage` (validacion y compatibilidad de versiones).

---

## Que NO debe incluir este esqueleto
- Logica de negocio concreta.
- Modelos o contratos especificos de cliente.
- Dependencias cloud especificas.
- UI o API.

## Resultado esperado
Un worker generico, limpio, extensible y documentado, que sirva como base para:
- workers simples de un solo paso,
- pipelines multi-paso desacoplados,
- ejecucion local, en contenedor o en Functions.
El codigo debe priorizar claridad y extensibilidad sobre optimizacion prematura.
