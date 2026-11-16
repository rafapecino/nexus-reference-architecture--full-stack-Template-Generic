# Arquitectura base de la maqueta

Esta seccion describe la arquitectura de referencia que acompaña a la maqueta. Sirve como punto de partida para cualquier proyecto derivado y debe adaptarse en `docs/architecture/<proyecto>` cuando existan particularidades de cliente o dominio.

## Vista logica

```
Frontend (Next.js) --> API Gateway/Reverse Proxy --> FastAPI (apps/api)
                                                \> Workers async (apps/worker-*)

FastAPI/Workers --> Capa de datos (packages/data: SQLAlchemy + Alembic)
                 \> Contratos (packages/contracts: Pydantic) [I/O tipado]
                 \> Utilidades comunes (packages/common: auth, logging, clientes externos)
                 \> Grafos IA (packages/ai: LangGraph)

Infra base: Postgres (db), Azurite (blob/queue), Redis opcional para cache/colas.
Observabilidad: logging estructurado y trazas integradas desde common.
```

## Componentes clave
- **API (FastAPI, apps/api)**: expone endpoints HTTP/JSON usando contratos compartidos. Routers delgados; logica en `application/`; adaptadores externos en `infrastructure/`.
- **Frontend (Next.js, apps/front)**: consume la API via `NEXT_PUBLIC_API_BASE_URL`; renderizado hibrido y manejo de sesiones de auth delegadas en la API.
- **Workers (apps/worker-*)**: tareas asincronas/cron que reutilizan `common`, `contracts` y `data` para mantenerse consistentes. Definicion de esqueleto en `docs/architecture/worker-skeleton.md`. Handlers/casos de uso en `application/`; triggers y conectores en `infrastructure/`.
- **Capa de datos (packages/data)**: modelos SQLAlchemy, sesiones unit-of-work y migraciones Alembic. Responsable de invariantes de persistencia e idempotencia en operaciones criticas.
- **Contratos (packages/contracts)**: DTOs Pydantic que definen entradas/salidas publicas (HTTP, colas, eventos) para minimizar divergencias entre API, front y workers.
- **Utilidades comunes (packages/common)**: autenticacion/autorizacion, clientes externos, logging y tracing. Diseñadas para ser puras e idempotentes cuando sea posible.
- **AI (packages/ai)**: esqueleto de LangGraph compartido para grafos IA (estado, tools, tracing) ejecutables desde API o como pasos dentro de un worker.
- **Infra base**: Postgres como fuente de verdad, Azurite/Azure Storage para blobs y colas; Redis o proveedor de colas puede añadirse segun caso de uso.

## Observabilidad y auditoría
- Logging estructurado con `common.logging` y `trace_id` propagado via middleware en la API.
- Contratos y modelos base para auditoría de conversación/LLM: ver `packages/contracts/src/contracts/audit_conversation.py` y modelos SQLAlchemy en `packages/data/src/data/models/audit_conversation.py`.
- Servicio de auditoría base en `apps/api/application/services/audit_conversation_service.py` para registrar conversaciones, mensajes y runs LLM (esqueleto ampliable por proyecto).
- Auditoría genérica de acciones (front/worker): contratos en `packages/contracts/src/contracts/audit_event.py`, modelo SQLAlchemy en `packages/data/src/data/models/audit_event.py` y servicio base en `apps/api/application/services/audit_event_service.py`.
- Integración con Azure Monitor/App Insights prevista: añade exportadores OpenTelemetry en `common` o en la API según proyecto (no se activa por defecto).

## Capas recomendadas (Clean Architecture)
- **domain/**: modelos y reglas puras, sin dependencias de infra.
- **application/**: casos de uso/servicios que orquestan repositorios, colas, LLM, etc.
- **infrastructure/**: adaptadores concretos (repos Postgres, Azure Storage, LLM provider, vector store, colas, triggers).
- **interfaces**: routers/controladores/presentacion que convierten I/O externos en comandos/queries del dominio.

En API y workers:
- Coloca casos de uso/servicios en `application/`.
- Coloca adaptadores de proveedor en `infrastructure/` (DB, colas, LLM, vector store).
- Los triggers/colas de worker son infraestructura; los handlers de negocio viven en application/domain.

## Reglas arquitectonicas y restricciones
- **Clean architecture**: routers/controladores orquestan; la logica de dominio vive en servicios/casos de uso; los repositorios abstraen el acceso a datos.
- **Type-first**: todos los limites (HTTP, mensajeria, storage) deben tiparse con contratos Pydantic o tipos TypeScript en el front; evita `Any` y convierte inputs externos a tipos internos cuanto antes.
- **Idempotencia**: endpoints y workers que mutan estado deben soportar reintentos seguros (claves idempotency, verificaciones previas, operaciones upsert). No asumir que una peticion se ejecuta una sola vez.
- **Separacion de contextos**: evitar dependencias directas entre front y data; cualquier cambio de schema debe reflejarse primero en contratos y migraciones.
- **Seguridad por defecto**: autenticacion obligatoria en rutas sensibles, secrets cargados via configuracion y jamas hardcodeados. Sanitiza entradas antes de tocar la base de datos o servicios externos.

## Patrones esperados
- **CQRS ligero**: consultas optimizadas separadas de comandos que mutan estado cuando el dominio lo requiera.
- **Eventos / outbox**: publicar eventos de dominio desde la capa de datos usando un patron outbox cuando sea necesario integrar con colas o websockets.
- **Repositorios**: encapsulan acceso a persistencia; la API y los workers dependen de interfaces, no de implementaciones concretas.
- **DTOs/Mapper**: conversion explicita entre modelos de persistencia y contratos publicos para mantener aislamiento de capas.

## Invariantes no negociables
- Sin logica de negocio en routers ni tareas programadas: siempre delegar en servicios/casos de uso testeables.
- Migraciones Alembic revisadas manualmente antes de aplicar en cualquier entorno.
- Toda API publica debe validar/serializar con contratos compartidos y documentarse con ejemplos de request/response.
- La API base expone `/messages` con contratos compartidos y errores estandar (`code`, `message`, `trace_id`, `detail`); respuestas 200 (sync) y 202 (async) segun modo de procesamiento.
- Observabilidad obligatoria: logs estructurados y, cuando aplique, tracing distribuido en API y workers.
- Modelos ORM solo en `packages/data/src/data/models/`; contratos compartidos (HTTP/colas/eventos) solo en `packages/contracts/src/contracts/`. No duplicar en `apps/*`.
- La documentacion de arquitectura debe mantenerse alineada con el codigo; cualquier cambio relevante se refleja aqui y en las variantes de proyecto.
