## interfaces

Puntos de entrada de la API: routers/controladores FastAPI, dependencias y validaciones de entrada.

Convenciones:
- Routers delgados: validar request, invocar casos de uso en `application/`, mapear a contratos de salida.
- No acceder directamente a infraestructura ni a modelos ORM; usar servicios/casos de uso.
- Si mantienes `apps/api/routers`, alinea su contenido con estas reglas (este directorio sirve de guia si creas nuevas rutas).
