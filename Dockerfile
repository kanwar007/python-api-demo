FROM ghcr.io/astral-sh/uv:0.13.0 AS uv
FROM python:3.14-slim

COPY --from=uv /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY app ./app

RUN groupadd --system app \
    && useradd --system --gid app --create-home app \
    && mkdir -p /app/logs \
    && chown app:app /app/logs

ENV PATH="/opt/venv/bin:$PATH"

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]