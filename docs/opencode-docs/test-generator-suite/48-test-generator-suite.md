# Test Generator Suite (TGS) — LLM-генератор API-тестов и тест-кейсов

## Источник

**Habr:** [ilya_akrickij](https://habr.com/ru/users/ilya_akrickij/) — [Как я сократил рутину QA до пары кликов: генератор API-тестов и тест-кейсов на LLM](https://habr.com/ru/articles/1038390/)  
**Репозиторий:** [gitlab.com/qa_ai/test-generator-suite](https://gitlab.com/qa_ai/test-generator-suite) (MIT)  
**Автор:** Илья Акрицкий, Manual QA (не разработчик — большая часть кода написана «как умею»)

## Проблема

QA-инженер тратит день на крупную фичу: прочитать требования в Confluence → зайти в Jira → посмотреть OpenAPI-спецификацию → разложить сценарии по шаблону → занести в Zephyr → открыть Postman → дописать проверки. 80% времени — механическое перекладывание информации из одной формы в другую.

## Возможности

TGS — монолитное FastAPI-приложение с тремя модулями:

```
┌──────────────────────────────────────────────────────┐
│                 Test Generator Suite                  │
├──────────────┬───────────────┬───────────────────────┤
│  API-тесты   │  Тест-кейсы   │    Doc Review         │
│              │               │                       │
│ OpenAPI →    │ Jira/Confluence│ Описание задачи →    │
│ Postman v2.1 │ → Zephyr/     │ Анализ полноты,      │
│ + Newman     │   TestRail/   │ тестируемости,        │
│   runner     │   TestIT      │ рисков               │
└──────────────┴───────────────┴───────────────────────┘
         │              │               │
         └──────────────┴───────────────┘
                         │
               Любой OpenAI-совместимый LLM
               (GPT-4o, Claude, DeepSeek, локальный)
```

### 1. API-тесты

- Указать Git-репозиторий с OpenAPI-спецификациями
- Выбрать нужные эндпоинты
- TGS клонирует репозиторий, разворачивает `$ref`-ссылки в единый документ
- Отправляет в LLM → получает Postman-коллекцию v2.1
- Коллекцию можно отредактировать в UI, запустить через Newman, закоммитить, скачать

### 2. Тест-кейсы

- Вписать описание задачи или номер Jira-тикета
- TGS подгружает описание из Jira + связанный контент из Confluence
- LLM возвращает структурированные тест-кейсы
- Одной кнопкой залить в Zephyr Scale, TestRail или TestIT
- Поддержка нескольких LLM одновременно (GPT-4o + DeepSeek, сравнение результатов)
- Feedback-петля: можно дать обратную связь и получить улучшенную версию

### 3. Doc Review

- Прогоняет описание задачи через LLM c промптом, оценивающим:
  - Полноту требований
  - Тестируемость каждого пункта
  - Потенциальные риски
- На выходе — отчёт с «дырами» в документации

## Архитектура

```
API-слой (tgs/api/)
  └── Валидация через Pydantic → вызов сервисов → маппинг ошибок в HTTP

Сервис-слой (tgs/services/)
  ├── openapi_bundler — рекурсивно разворачивает $ref (кроме циклических и HTTP)
  ├── postman_generator — собирает payload для LLM + парсит ответ (срез markdown-блоков)
  └── testcase_parser — парсит Markdown-подобный формат в структуру для UI и TMS

LLM-слой (tgs/llm/)
  └── OpenAI-совместимый клиент. Добавление модели = 6 строк в config.yaml

TMS-слой (tgs/tms/)
  └── Базовый интерфейс TestManagementClient
  └── Реализации: Zephyr Scale, TestRail, TestIT (TestRail/TestIT не тестировались)

Интеграции (tgs/integrations/)
  └── Jira — подгрузка тикетов
  └── Confluence — подгрузка связанной документации
```

### Конфигурация

Три источника с приоритетом: env → `config.yaml` → `config.example.yaml`.  
Типизирована через `pydantic-settings`. Секреты обёрнуты в `pydantic.SecretStr` (не попадают в логи через `repr()`/`str()`).

```yaml
models:
  gpt4:
    name: "GPT-4"
    base_url: "https://api.openai.com/v1"
    model_name: "gpt-4o"
    temperature: 0.7
    enabled: true
```

## Деплой

| Сценарий | Команда |
|----------|---------|
| Dev/одиночное | `docker compose up -d` |
| Локальная разработка | `pip install -e .` → `tgs serve` |
| Production | Образ + Helm-чарт → кластер |

По умолчанию слушает `127.0.0.1`. Для внешнего доступа — reverse-proxy (nginx, Caddy, Traefik) с TLS.

## Стек

- **Backend:** Python 3.10+, FastAPI, pydantic, pydantic-settings, httpx, GitPython, PyYAML
- **Frontend:** Чистый HTML/JS без фреймворков
- **LLM:** Любой OpenAI-совместимый (публичный API или локальный через vLLM/Ollama)
- **TMS:** Zephyr Scale, TestRail, TestIT (REST API)
- **Atlassian:** Jira, Confluence (REST API)
- **Test runner:** Newman (опционально)
- **Линт/типы/тесты:** ruff, mypy, pytest

## Выводы автора

- LLM в QA хороша не когда заменяет тестировщика, а когда снимает рутину
- Сгенерированные тест-кейсы всегда требуют ревью
- Качество сильно зависит от модели: GPT-4o / Claude 3.5 Sonnet — достойно, локальные модели — плохо
- Рабочий день QA → 15-20 минут вместе с ревью
- Даже Manual QA без бэкенд-бэкграунда может собрать инструмент под свою боль

## Relevance

Прямой референс для spec-driven AGENTS.md. TGS решает ту же задачу, что и GSD-цикл в интерпретации для QA: требования → агент → тесты → проверка. Архитектура (один эндпоинт → bundler → LLM → парсер → TMS) хорошо ложится на AGENTS.md с `instructions` URL.
