FROM python:3.12-slim

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY requirements-prod.txt .
COPY wheels/ wheels/
RUN uv venv && uv pip install --no-index --find-links wheels/ -r requirements-prod.txt

COPY . .
RUN uv pip install --no-index --find-links wheels/ --no-deps -e .

EXPOSE 8000

CMD ["bash", "./run.sh"]
