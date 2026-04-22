# PDF Parser

Проект конвертирует PDF-документы в очищенный Markdown, комбинируя два источника:

- **Marker** — для базового извлечения текста в Markdown.
- **Docling** — для извлечения таблиц и изображений с подписями.

На выходе проект формирует:

- `.md` файл для каждого PDF;
- папку `_image/` с извлечёнными изображениями;
- ZIP-архив с результатами.

---

## Архитектура решения

```text
PDF files
   │
   ├── Marker CLI ──> raw markdown ──> cleaning.py
   │
   └── Docling ──> tables + pictures + captions
                         │
                         └── markdown.py
                                  │
                                  ▼
                         merged final markdown
                                  │
                                  ▼
                         output/*.md + _image/* + submission.zip
```

### Краткое описание модулей

- `cli.py` — точка входа и разбор аргументов командной строки.
- `config.py` — конфигурация приложения через `dataclass`.
- `pipeline.py` — orchestration-слой: запускает весь конвейер по файлам.
- `marker_runner.py` — изолированная работа с внешним CLI `marker_single`.
- `docling_adapter.py` — извлечение таблиц и изображений через Docling.
- `cleaning.py` — очистка Markdown от HTML, шума и повторов.
- `markdown.py` — конвертация таблиц в Markdown и вставка изображений.
- `exceptions.py` — проектные исключения.
- `logging_utils.py` — централизованная настройка логирования.

---

## Структура репозитория

```text
pdf_parser_repo/
├── README.md
├── pyproject.toml
├── src/
│   └── pdf_parser/
│       ├── __init__.py
│       ├── cli.py
│       ├── cleaning.py
│       ├── config.py
│       ├── docling_adapter.py
│       ├── exceptions.py
│       ├── logging_utils.py
│       ├── markdown.py
│       ├── marker_runner.py
│       └── pipeline.py
└── tests/
    ├── test_cleaning.py
    └── test_markdown.py
```

---

## Требования

- Python 3.11+
- установленный `marker_single` в `PATH`
- зависимости Python из `pyproject.toml`

---

## Установка

### 1. Клонировать репозиторий

```bash
git clone <repo_url>
cd pdf_parser_repo
```

### 2. Установить зависимости

Через `pip`:

```bash
pip install -e .
```

Для разработки:

```bash
pip install -e .[dev]
```

---

## Подготовка входных данных

Сложите PDF-файлы в папку `./pdfs`.

По умолчанию обрабатываются файлы по шаблону:

```text
document_*.pdf
```

---

## Запуск

Базовый запуск:

```bash
pdf-parser --input-dir ./pdfs --output-dir ./output
```

Пример запуска с дополнительными параметрами:

```bash
pdf-parser \
  --input-dir ./pdfs \
  --output-dir ./output \
  --archive-name submission \
  --pdf-pattern "document_*.pdf" \
  --marker-timeout-sec 600 \
  --log-level INFO
```

Запуск без OCR:

```bash
pdf-parser --input-dir ./pdfs --output-dir ./output --no-ocr
```

Оставить временные директории для отладки:

```bash
pdf-parser --input-dir ./pdfs --output-dir ./output --keep-temporary-dirs
```

Остановиться на первой ошибке:

```bash
pdf-parser --input-dir ./pdfs --output-dir ./output --fail-fast
```

---
