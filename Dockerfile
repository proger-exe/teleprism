FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
RUN uv sync --no-dev

COPY teleprism ./teleprism

CMD ["uv", "run", "--no-dev", "teleprism"]
