# 1. build — инсталира зависимости
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# 2. runtime — само каквото трябва
FROM python:3.12-slim

WORKDIR /app

# Копирай инсталираните пакети от builder
COPY --from=builder /install /usr/local

# Копирай проекта
COPY . .

EXPOSE 5000

# gunicorn стартира от /app, така че validation_chain/ е видим
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "wsgi:app"]
