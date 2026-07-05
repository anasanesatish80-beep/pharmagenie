FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

RUN useradd --create-home --shell /bin/bash appuser

COPY requirements.txt pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn pharmagenie.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
