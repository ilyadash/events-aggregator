FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml .
RUN uv pip install --no-cache -e ".[dev]"

COPY . .

EXPOSE 8000

CMD ["bash", "./run.sh"]
