# Doc Validator

Проект за валидация на документи (фактура, доклад и заявка за материали), реализиран на Python. Проектът демонстрира прилагането на два шаблона за дизайн: **Chain of Responsibility** (верига отговорности) и **Visitor** (посетител).

## Функционалности

- **CLI интерфейс** за бърза валидация на файлове от терминала.
- **Уеб интерфейс (Flask)** с форма за въвеждане на път до файл или директно качване на файл (upload).
- **JSON API** за програмна валидация чрез HTTP POST заявки.
- **Docker контейнер** за лесен деплой и стартиране с една команда.
- **Документация** (HTML и DOCX), генерирана автоматично чрез Sphinx и PlantUML.

## Структура на проекта

```text
doc_validator/
├── documents/          # Модели на документите (Фактура, Доклад, Заявка)
├── parsing/            # Парсери за JSON и CSV файлове
├── validation_chain/   # Chain of Responsibility шаблон
├── visitors/           # Visitor шаблон (Валидация, Резюме, Експорт)
├── server/             # Flask приложение (уеб интерфейс и API)
├── samples/            # Примерни файлове (валидни и невалидни)
├── docs/               # Sphinx документация (HTML и DOCX)
├── main.py             # CLI входна точка
├── wsgi.py             # WSGI входна точка за gunicorn (Docker)
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Конфигурация за Docker Compose
└── requirements.txt    # Python зависимости
```

## Технологии

- **Python 3.12+**
- **Flask** — уеб сървър и API
- **Gunicorn** — WSGI сървър за продукционна среда
- **Docker** — контейнеризация
- **Sphinx** + **PlantUML** + **docxbuilder** — генериране на документация

## Инсталация и стартиране (локално)

1. Клонирайте репозиторито и влезте в папката:

   ```bash
   cd doc_validator
   ```

2. Създайте виртуална среда и я активирайте:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Инсталирайте зависимостите:

   ```bash
   pip install -r requirements.txt
   ```

   Ако смятате да генерирате документацията, инсталирайте и `requirements-dev.txt`.

### Стартиране през CLI

```bash
python main.py samples/invoice_ok.json
python main.py samples/invoice_bad.json samples/report_ok.json
```

### Стартиране на уеб сървъра

```bash
python -m server.app
```

Отворете `http://localhost:5000` в браузър, за да достъпите уеб интерфейса. Документацията е достъпна на `http://localhost:5000/docs/`.

## Стартиране с Docker

Най-лесният начин да стартирате проекта (включително уеб интерфейса и документацията) е чрез Docker Compose:

```bash
docker compose up --build
```

След като контейнерът стартира, приложението е достъпно на:

- **Уеб интерфейс:** `http://localhost:5000/`
- **Документация:** `http://localhost:5000/docs/`
- **Health check:** `http://localhost:5000/health`

### HTTP API

Валидация на файл по име:

```bash
curl -X POST http://localhost:5000/validate \
  -H "Content-Type: application/json" \
  -d '{"filename": "samples/invoice_ok.json"}'
```

Валидация чрез качване на файл:

```bash
curl -F "file=@samples/invoice_ok.json" http://localhost:5000/validate/upload
```

## Генериране на документация

Документацията използва Sphinx и PlantUML. За да я генерирате, уверете се, че имате инсталирани `requirements-dev.txt` и системния пакет `plantuml`.

```bash
cd docs

# HTML документация
sphinx-build -b html source build/html

# DOCX документация (за copy-paste в шаблон)
sphinx-build -b docx source build/docx
```

## Използвани шаблони за дизайн

### 1. Chain of Responsibility

Заявката за валидация минава през поредица от независими проверки (съществуване на файл, формат, парсване, тип, съдържание). Всяка проверка може да спре веригата при грешка.

### 2. Visitor

Използва се за операции над готовия документ. Позволява добавянето на нови операции (валидация, резюме, експорт) без промяна на класовете на самите документи.
