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

## Что было улучшено относительно однострочного скрипта

1. **Модульность** — логика разделена по слоям, а не лежит в одном файле.
2. **PEP 8 и читаемость** — type hints, docstrings, сортировка импортов, меньшие функции.
3. **Обработка ошибок** — убран bare `except`, добавлены проектные исключения и осмысленные сообщения.
4. **Воспроизводимость** — конфиг вынесен в `AppConfig`, поведение задаётся через CLI-параметры.
5. **Переиспользуемость** — отдельные компоненты можно использовать независимо.
6. **Тестируемость** — добавлены простые unit-тесты для функций без внешних зависимостей.
7. **Поддерживаемость** — централизованное логирование и явная структура проекта.

---

## Проверка качества

### Ruff

```bash
ruff check .
```

### Pytest

```bash
pytest
```

### Mypy

```bash
mypy src
```

---

## Ограничения текущего решения

- качество зависит от внешних инструментов `Marker` и `Docling`;
- привязка изображений к подписям работает по эвристике: картинка должна идти перед текстовым блоком-подписью;
- нестандартные таблицы с очень сложным `rowspan/colspan` могут потребовать дополнительной логики постобработки.
