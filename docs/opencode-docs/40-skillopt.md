# SkillOpt — автоматическая оптимизация AGENTS.md

> **Источник:** https://microsoft.github.io/SkillOpt/  
> **Paper:** https://arxiv.org/abs/2605.23904  
> **Code:** https://github.com/microsoft/SkillOpt  
> **Видео:** https://youtu.be/JUBMDTCiM0M

SkillOpt — training loop, который улучшает markdown-скилл (AGENTS.md) через rollout'ы, рефлексию и bounded edits. Целевая модель **frozen** (веса не меняются), оптимизируется только текст инструкций.

---

## Как это работает

```
1. Target model с current skill выполняет таски → rollout с оценками
2. Optimizer анализирует успехи/неудачи → bounded edits в skill
3. Validation gate: принять правку только если held-out лучше
4. Экспорт best_skill.md
```

- **Target model** — любая модель через API (frozen)
- **Optimizer model** — отдельная модель, которая пишет правки
- **Skill** — plain markdown (наш AGENTS.md)
- **Bounded edits** — текстовый learning rate: правки ограничены по объёму, без полной перезаписи

---

## Установка

```bash
git clone https://github.com/microsoft/SkillOpt.git
cd SkillOpt
pip install -r requirements.txt
```

---

## Конфигурация

SkillOpt настраивается через config-файлы (YAML/JSON). Пример для OpenCode-совместимого запуска:

```yaml
# config.yaml
target:
  model: "deepseek-v4-flash-free"     # или gpt-4o, claude-3.5-sonnet
  provider: "openai-compatible"       # openai, anthropic, openai-compatible
  api_key: "${TARGET_API_KEY}"
  api_base: "https://api.deepseek.com/v1"  # для openai-compatible

optimizer:
  model: "gpt-5.5"                    # оптимизатор: модель, которая пишет правки
  provider: "openai"
  api_key: "${OPTIMIZER_API_KEY}"

skill:
  initial: "AGENTS.md"                # стартовый skill — наш AGENTS.md
  output: "best_skill.md"

benchmark:
  name: "spreadsheetbench"            # или searchqa, office, docvqa, livemath, alfworld
  split: "train"
  n_tasks: 50

training:
  max_epochs: 10
  batch_size: 8
  edit_budget: 3                      # bounded edits: макс. число правок за шаг
  validation_split: 0.2               # 20% задач — held-out gate
```

### Параметры bounded edits

| Параметр | Значение | Эффект |
|---|---|---|
| `edit_budget: 1` | Консервативно | Медленно, но стабильно |
| `edit_budget: 3` | Default | По 3 правила за шаг |
| `edit_budget: 5+` | Агрессивно | Быстро, но риск регрессий |

---

## Запуск

```bash
# Базовый запуск
python run.py --config config.yaml

# Resume после остановки
python run.py --config config.yaml --resume

# Только eval на готовом skill
python run.py --config config.yaml --eval-only --skill best_skill.md
```

---

## Вывод: best_skill.md

После обучения SkillOpt генерирует `best_skill.md` — оптимизированную версию AGENTS.md. Это plain markdown, можно скопировать в корень проекта.

```bash
cp output/best_skill.md /my-project/AGENTS.md
```

SkillOpt также выводит:
- `output/train_log.csv` — метрики по эпохам
- `output/edits/` — история всех предложенных правок (accepted/rejected)
- `output/rollouts/` — трассы rollout'ов для анализа

---

## SkillOpt в связке с OpenCode

```
  1. Базовый AGENTS.md (ручной)
  2. SkillOpt: rollout'ы на V4 flash → bounded edits → best_skill.md
  3. best_skill.md → копия в AGENTS.md проекта
  4. OpenCode использует оптимизированный AGENTS.md
```

### Выбор моделей

| Роль | Модель | Комментарий |
|---|---|---|
| Target | V4 flash free (frozen) | Бесплатно, достаточно для rollout'ов |
| Target | GPT-5.5, Claude 4, Qwen | Если нужна максимальная точность |
| Optimizer | GPT-5.5 (рекомендуется) | У них в статье — GPT-5.5 даёт лучшие правки |
| Optimizer | V4 flash free | Можно, но правки будут проще |
| Optimizer | Claude 4 Sonnet | Хорошая альтернатива GPT-5.5 |

Настройка `edit_budget` под твой сценарий:
- **Для начала:** `edit_budget: 2`, `max_epochs: 5` — быстро попробовать
- **Для production:** `edit_budget: 3`, `max_epochs: 10-20` — стабильное улучшение
- **SkillOpt + lessons.md:** если в `AGENTS.md` включён раздел lessons из examples/08, SkillOpt сам найдёт какие уроки работают, а какие нет

---

## Transfer: перенос skill между моделями

SkillOpt поддерживает transfer без переобучения:

```bash
# Обучили на GPT-5.4 → переносим на V4 flash
python run.py --eval-only --skill best_skill.md \
  --target-model deepseek-v4-flash-free
```

По статье: cross-model transfer даёт +15.2%, cross-harness +31.8%.

---

## Требования

- **Python 3.10+**
- Доступ к API целевой модели и оптимизатора
- `OPENAI_API_KEY` (для GPT-оптимизатора)
- Для openai-compatible моделей: `api_base` в конфиге

---

## Ограничения

- Optimizer должен быть **умнее или равен** target в анализе — иначе будет генерировать плохие правки
- Bounded edits не панацея: если skill изначально плохой, оптимизация может не помочь
- Зависит от качества benchmark'а: плохой benchmark → плохой skill
- На данный момент поддерживает 6 benchmark'ов (SearchQA, SpreadsheetBench, Office, DocVQA, LiveMath, ALFWorld) — для кастомных сценариев нужна адаптация
