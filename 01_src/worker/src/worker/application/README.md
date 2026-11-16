## application

Casos de uso/servicios del worker: coordinan handlers/pasos, dominio y adaptadores. No deben depender de triggers ni de detalles de cola.

Convenciones:
- Mantener aqui la orquestacion de negocio; los triggers solo construyen `WorkerMessage` y delegan.
- Depender de interfaces/puertos; las implementaciones concretas viven en `infrastructure/`.
- Si se integra un grafo LangGraph, envolverlo aqui como parte del flujo de negocio (no en triggers).
