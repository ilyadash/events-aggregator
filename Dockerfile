FROM python:3.12-slim

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml .
RUN uv sync

COPY . .

EXPOSE 8000

CMD ["bash", "./run.sh"]
