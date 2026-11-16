# Reglas de modelos ORM

Estas reglas aplican a toda la carpeta `data/models` y a todas sus subcarpetas (incluyendo `staging`).
Su objetivo es evitar errores de imports, relaciones y migraciones.

## Convenciones obligatorias

1. Clase ORM en `PascalCase`.
- Ejemplo: `class ContenidoFicha(Base)`.

2. `__tablename__` en `snake_case` y estable.
- Ejemplo: `__tablename__ = "contenido_ficha"`.

3. Archivo en `snake_case.py`.
- Ejemplo: `contenido_ficha.py`.

4. Campos y atributos en `snake_case`.
- Ejemplo: `fecha_generacion`, `ficha_estructura_id`.

5. `relationship()` usando nombre real de clase (string en PascalCase).
- Correcto: `relationship("FichaEstructura", back_populates="contenidos")`.
- Evitar: `relationship("fichaestructura", ...)`.

6. `ForeignKey` debe referenciar tabla/columna real, no nombre de clase.
- Correcto: `ForeignKey("staging_fichas_estructura.id")`.

7. Registrar todos los modelos en `data/models/__init__.py`.
- Importar desde modulo real.
- Exponer en `__all__`.

## Compatibilidad temporal

Si se renombra una clase, mantener alias temporal para no romper imports existentes.

Ejemplo:
```python
class ContenidoFicha(Base):
    ...

contenidoficha = ContenidoFicha
```

Eliminar alias cuando todo el codigo consumidor use la clase nueva.

## Checklist antes de crear migracion

1. Verificar que el modelo nuevo este importado en `data/models/__init__.py`.
2. Ejecutar `python -m alembic heads` desde `01_src/packages/data`.
3. Generar revision: `alembic revision --autogenerate -m "mensaje"`.
4. Revisar script generado en `migrations/versions/`.
5. Aplicar: `alembic upgrade head`.
