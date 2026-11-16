## interfaces

Puntos de entrada del worker (triggers, CLI) y handlers visibles para el runtime.

Convenciones:
- Los triggers construyen `WorkerMessage` y delegan en casos de uso en `application/`.
- Los handlers que procesan pasos se alinean con `application/`; evita poner logica en el trigger.
- Mapear entradas/salidas usando contratos de `packages/contracts`; no acceder directo a ORM ni SDKs desde aqui.
