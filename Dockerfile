# Stage 1: Build
FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=3.14 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev --no-install-project

# ==========================================
# Stage 2: Development
# ==========================================
FROM python:3.14-slim AS dev

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON=3.14

WORKDIR /app

COPY --from=build /opt/venv /opt/venv
COPY pyproject.toml uv.lock* ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN uv sync --frozen --group dev --no-install-project
# ==========================================
# Stage 3: Production
# ==========================================
FROM python:3.14-slim AS prod

# uv is NOT needed in production, keeping the final image as small as possible
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=4

WORKDIR /app

# Copy the production venv from the build stage
COPY --from=build /opt/venv /opt/venv

# Copy the application source code
COPY . .

# Security: Create a non-root user and switch to it
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run with multiple workers for production concurrency
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}"]


