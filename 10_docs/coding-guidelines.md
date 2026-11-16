# Plantilla de guías de codificación

Usa esta plantilla para documentar las convenciones de código y pruebas del repositorio. Completa cada sección con las reglas específicas de tu proyecto o cliente.

## Qué contiene

- **Convenciones de estilo**: nombres de archivos y carpetas, snake_case vs camelCase, patrones para tests y fixtures, comentarios y documentación.
- **Cómo deben generarse tests**: niveles (unitarios, integración, contract), herramientas, precondiciones, datos de ejemplo y criterios de aceptación.
- **Reglas específicas de tu stack**: linters, formateadores, tipado, frameworks y restricciones de dependencias.
- **Organización del proyecto**: dominios/DDD, capas, carpetas por bounded context, políticas de módulos compartidos.

## Para qué sirve

- Para que la IA genere código que encaje perfectamente con tu repo.
- Para evitar inconsistencias cuando el repositorio crece.

## Plantilla sugerida

1. **Resumen rápido**
   - 3-5 bullets con las normas clave innegociables.
2. **Nombres y organización**
   - Patrones de carpetas, sufijos/prefijos, convenciones de importación.
3. **Estilo y formato**
   - Herramientas (ruff/black, eslint/prettier, mypy, etc.) y flags obligatorios.
4. **Tipado y validaciones**
   - Reglas *type-first*, tipos prohibidos, estrategias de nullability y validación de entrada/salida.
5. **Patrones de arquitectura**
   - Capas (por ejemplo, clean architecture), dependencia invertida, boundaries y anti-patrones a evitar.
6. **Pruebas y calidad**
   - Tipos de tests, estructura de carpetas, cómo aislar dependencias, cobertura mínima, datos semilla.
7. **Seguridad y observabilidad**
   - Reglas de autenticación/autorización, logging, métricas y trazas.
8. **Ejemplos**
   - Snippets representativos de controladores, servicios, repositorios y componentes front.

> Duplica este archivo para cada proyecto si necesitas variantes específicas: `docs/projects/<proyecto>/coding-guidelines.md`.
