# Contributing

## Flujo de trabajo

1. Crea una rama desde `main`: `git checkout -b feat/nombre-feature`
2. Realiza tus cambios siguiendo las guías de estilo del proyecto.
3. Ejecuta los tests: `pytest`
4. Abre un Pull Request describiendo los cambios.

## Guías de estilo

- Python: seguir PEP 8, formatear con `black`, lint con `ruff`.
- Commits: usar [Conventional Commits](https://www.conventionalcommits.org/).

## Revisión de código

- Todo PR requiere al menos 1 aprobación.
- Los checks de CI deben pasar antes de mergear.
