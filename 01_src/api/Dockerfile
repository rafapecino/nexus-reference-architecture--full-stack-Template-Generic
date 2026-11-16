FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# Dependencias del runtime (sin toolchain de build).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

# Toolchain de compilación para deps con extensiones.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copiamos metadata y lock para cachear resoluciones.
COPY pyproject.toml uv.lock ./
COPY packages/common/pyproject.toml packages/common/pyproject.toml
COPY packages/data/pyproject.toml packages/data/pyproject.toml
COPY packages/contracts/pyproject.toml packages/contracts/pyproject.toml
COPY packages/ai/pyproject.toml packages/ai/pyproject.toml
COPY apps/api/pyproject.toml apps/api/pyproject.toml
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml

# Copiamos codigo necesario de los paquetes/workspace (dependencias locales).
COPY packages/common packages/common
COPY packages/data packages/data
COPY packages/contracts packages/contracts
COPY packages/ai packages/ai
COPY apps/api apps/api

# Instala solo el paquete API y sus deps desde el lock (sin dev).
RUN uv sync --frozen --no-dev --package api --directory /app

FROM base AS runtime

WORKDIR /app/apps/api

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages /app/packages
COPY --from=builder /app/apps/api /app/apps/api

ENV PATH="/app/.venv/bin:${PATH}"
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
