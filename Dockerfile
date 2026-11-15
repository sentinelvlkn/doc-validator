# 1. build — инсталира runtime зависимости (Flask + gunicorn)
FROM python:3.12-slim AS pybuilder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# 2. docs — инсталира Sphinx + PlantUML и билдва HTML документацията
FROM python:3.12-slim AS docbuilder
WORKDIR /app

# PlantUML изисква Java, затова инсталираме и двете. 
RUN apt-get update && \
    apt-get install -y --no-install-recommends plantuml && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .
RUN cd docs && sphinx-build -b html source build/html


# 3. runtime — само нужното за работа
FROM python:3.12-slim
WORKDIR /app

COPY --from=pybuilder /install /usr/local
COPY . .
COPY --from=docbuilder /app/docs/build/html /app/docs_html

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "wsgi:app"]
