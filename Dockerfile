FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --target=/app/dependencies -r requirements.txt


FROM python:3.10-slim AS runtime

WORKDIR /app

COPY --from=builder /app/dependencies /app/.local

ENV PATH=/app/.local/bin:$PATH \
    PYTHONPATH=/app/.local:$PYTHONPATH

COPY . .

EXPOSE 3000
