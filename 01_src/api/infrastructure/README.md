## infrastructure

Adaptadores concretos para la API: repositorios sobre Postgres, clientes de colas o proveedores (LLM, vector store, storage), y wiring de configuracion.

Convenciones:
- Implementar aqui las interfaces/puertos definidos en `application/` o `domain/`.
- Encapsular detalles de librerias (SQLAlchemy, SDK Azure, etc.) para mantener limpio el dominio.
- No incluir logica de negocio; solo acceso y adaptacion.
