# ==========================================
# Stage 1: Build (Production Dependencies)
# ==========================================
FROM python:3.12-slim AS build

# Inject the official uv binary into the image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Optimize uv for Docker: compile bytecode and use copy mode for faster, cache-friendly installs
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy dependency files first to leverage Docker layer caching
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install ONLY production dependencies
RUN uv venv /opt/venv && \
    uv sync --frozen --no-dev --no-install-project


# ==========================================
# Stage 2: Development
# ==========================================
FROM python:3.12-slim AS dev

# uv is needed in dev to install dev-dependencies and run scripts
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the production venv from the build stage
COPY --from=build /opt/venv /opt/venv

# Copy dependency files to install development dependencies (pytest, ruff, etc.)
COPY pyproject.toml uv.lock* ./

# Install development dependencies
RUN uv sync --frozen --group dev --no-install-project

# Copy the application source code
COPY . .

EXPOSE 8000

# Run with hot-reloading enabled
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# ==========================================
# Stage 3: Production
# ==========================================
FROM python:3.12-slim AS prod

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


