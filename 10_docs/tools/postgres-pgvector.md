# PostgreSQL + pgvector

Guía de uso de la extensión `pgvector` en este proyecto.

---

## ¿Qué es pgvector?

`pgvector` es una extensión de PostgreSQL que añade soporte nativo para **vectores de búsqueda semántica**. Permite almacenar y consultar embeddings (representaciones numéricas de textos, imágenes, etc.) directamente en la base de datos, sin necesidad de un servicio externo como Pinecone o Qdrant.

En este proyecto se usa para almacenar los embeddings generados por el paquete `packages/ai` y realizar búsquedas por similitud sobre los documentos del datalake.

---

## Configuración en este proyecto

### Imagen Docker

El contenedor de PostgreSQL usa la imagen oficial con pgvector preinstalada:

```yaml
# docker-compose.yml
image: pgvector/pgvector:pg16
```

### Activación de la extensión

La extensión se activa automáticamente al ejecutar las migraciones de Alembic:

```python
# migrations/versions/72caee442359_init.py
op.execute("CREATE EXTENSION IF NOT EXISTS vector")
```

Si necesitas activarla manualmente:

```bash
docker exec -it postgres_db psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

---

## Comandos de verificación

### Comprobar que pgvector está instalada

```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

Devuelve una fila con los metadatos de la extensión (nombre, versión, esquema...).
Si no devuelve ninguna fila, la extensión no está activada en esta base de datos.

### Consultar la versión instalada

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

Devuelve solo el número de versión, por ejemplo `0.8.0`.
Útil para confirmar que la versión instalada es compatible con las funcionalidades que usa el proyecto.

---

## Reset completo del entorno local

Si necesitas partir de cero (borra todos los datos):

```bash
docker compose down -v
docker compose up -d db
cd 01_src/packages/data
alembic upgrade head
```

## Actualizar el contenedor sin perder datos

Si ya tenías el contenedor corriendo con `postgres:16` y quieres actualizar a `pgvector/pgvector:pg16`:

```bash
docker compose down
docker compose pull db
docker compose up -d db
```

Luego activa la extensión manualmente si el volumen ya existía:

```bash
docker exec -it postgres_db psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```
