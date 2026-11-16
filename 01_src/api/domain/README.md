## domain

Modelos y reglas de negocio puras de la API. Sin dependencias de FastAPI, BD, colas ni proveedores externos.

Convenciones:
- Tipar con Pydantic/typing. Sin importar infrastructure ni adapters.
- Colocar invariantes y validaciones propias del dominio aqui.
- Usar contratos compartidos (packages/contracts) solo en los bordes; dentro del dominio preferir tipos internos.
