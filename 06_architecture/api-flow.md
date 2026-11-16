# Flujo de la API (FastAPI)

Este diagrama describe el recorrido principal de una petición HTTP en la API: entrada por FastAPI, middleware de trazabilidad, routers, servicios de aplicación y acceso a PostgreSQL.

## Diagrama

```mermaid
flowchart LR
  A[Cliente HTTP\nSwagger / Front / curl] --> B[FastAPI app\napps/api/main.py]
  B --> C[TraceIdMiddleware\ninterfaces/middleware/trace.py]
  C --> D[Routers\ninterfaces/routers]

  D --> E[/health]
  D --> F[/version]
  D --> G[/db/ping]
  D --> H[/items/*]
  D --> I[/messages]

  H --> J[ItemService\napplication/services/item.py]
  J --> K[BaseService\napplication/services/base.py]
  K --> L[(SQLAlchemy Session)]
  L --> M[(PostgreSQL)]

  I --> N[MessageService\napplication/services/message_service.py]
  N --> O[MessageEngine\napplication/services/message_engine.py]
  O --> P[MessageResponse]

  N -->|AUDIT_ENABLED=true| Q[AuditConversationService / AuditEventService]
  Q --> L

  B --> R[Exception handlers\ninterfaces/errors.py]
  R --> S[ErrorResponse + trace_id]
```

## Notas rápidas

- Los routers deben mantenerse delgados: validan entrada, delegan a servicios y mapean salida.
- La lógica de negocio/orquestación vive en `application/services`.
- La conexión a BD se resuelve vía `data.database` y configuración centralizada de `common.config.settings`.
- El `trace_id` se propaga por middleware y se devuelve en respuesta para trazabilidad.
