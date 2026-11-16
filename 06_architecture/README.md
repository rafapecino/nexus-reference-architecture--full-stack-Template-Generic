# architecture
Diagramas, decisiones tecnicas (ADRs), notas de despliegue, ...

Antes de crear variantes por proyecto, rellena la plantilla base en `../architecture.md` con la vista general del sistema.

## Estructura sugerida
- **Base de la maqueta**: documentos comunes (por ejemplo, `docs/architecture/adr-plantilla.md` o diagramas de referencia) que aplican a cualquier proyecto derivado.
- **Flujo API FastAPI**: ver `api-flow.md` para el recorrido request -> router -> service -> BD.
- **Workers genericos**: ver `worker-skeleton.md` para el esqueleto de worker infra-agnostico, triggers, reintentos y registro de handlers.
- **Grafo IA (LangGraph)**: usar `packages/ai` como base compartida para definir estado, nodos/tools y tracing de grafos IA (ejecutable desde API o worker segun necesidad).
- **Variantes por proyecto**: subcarpetas `docs/architecture/<proyecto>/` con ADRs y diagramas especificos del cliente/implantacion.

## Fuentes de verdad (no duplicar)
- Modelos ORM: siempre en `packages/data/src/data/models/`; prohibido declararlos en `apps/*`.
- Contratos compartidos (API, colas, eventos): siempre en `packages/contracts/src/contracts/`; los servicios y workers importan desde ahi.
