FROM python:3.11-slim

ARG LOCAL_USER_ID=1000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Fix for apt hash sum mismatch errors
RUN echo "Acquire::http::Pipeline-Depth 0;" > /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::http::No-Cache true;" >> /etc/apt/apt.conf.d/99custom && \
    echo "Acquire::BrokenProxy    true;" >> /etc/apt/apt.conf.d/99custom

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# User privileges for security
RUN adduser --disabled-password --gecos '' --uid $LOCAL_USER_ID appuser

# Install workspace-mcp package
RUN uv pip install --system workspace-mcp>=1.5.5

# Copy application files
COPY main.py ./

# Create credentials directory for OAuth tokens
RUN mkdir -p /app/.credentials && chown -R appuser:appuser /app

ENV APP_PORT=8001 \
    APP_HOSTNAME=0.0.0.0

EXPOSE 8001

# Healthcheck for MCP server
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/mcp || exit 1

USER appuser

CMD ["python", "main.py"]
