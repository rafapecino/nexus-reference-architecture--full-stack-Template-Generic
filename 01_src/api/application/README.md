## application

Casos de uso/servicios de la API: orquestan dominio, repositorios y adaptadores externos. No exponen detalles HTTP ni de infraestructura.

Convenciones:
- No poner logica en routers; todo flujo se implementa aqui y se invoca desde interfaces.
- Depender de interfaces/puertos (repositorios, clientes) definidos en dominio/application; las implementaciones concretas viven en `infrastructure/`.
- Mantener funciones/metodos puramente sincronos o async segun necesidad, pero sin acoplar a FastAPI.
