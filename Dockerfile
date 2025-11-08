# ---------- Stage 1: build environment ----------
# Base image with uv + Python
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS build

WORKDIR /app

# Copy project metadata (pyproject + lock) first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtualenv (no dev dependencies)
RUN uv sync --frozen --no-cache --no-dev

# Copy the actual source code
COPY src ./src

# ---------- Stage 2: runtime image ----------
FROM python:3.12-slim AS run

WORKDIR /app

# Copy virtualenv and source from build stage
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/src ./src

# Add venv to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy your env if you plan to run locally (optional)
# COPY .env ./.env

# Default command: run your MCP server
CMD ["python", "-m", "etl_mcp_serv.core.main"]
