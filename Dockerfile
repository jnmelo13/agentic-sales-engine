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
# Create a new user named 'appuser' with no home directory and no system group
RUN adduser --disabled-password --gecos '' --uid $LOCAL_USER_ID appuser

# Copy dependency files and source code (needed for uv sync to build the package)
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/
COPY main.py ./

# Install Python dependencies using uv (as root, before switching user)
RUN uv sync --frozen --no-dev

ENV APP_PORT=7860

EXPOSE 7860

# Healthcheck for Gradio application
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${APP_PORT}/ || exit 1

# Change ownership to the new user
RUN chown -R appuser:appuser /app
USER appuser

CMD ["uv", "run", "python", "main.py"]
