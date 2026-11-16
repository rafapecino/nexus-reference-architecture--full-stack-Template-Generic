## domain

Modelos y reglas puras del dominio que procesa el worker. Sin dependencias de triggers, BD ni SDKs de proveedor.

Convenciones:
- Tipar con Pydantic/typing; sin importar adapters concretos.
- Colocar invariantes y validaciones propias del proceso aqui.
- Mantenerlo reutilizable entre handlers/pasos.
