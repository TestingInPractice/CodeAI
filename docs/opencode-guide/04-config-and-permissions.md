# Конфиг и разрешения

**Глава 04**

---

## Почему `opencode.json` — это control plane

Проектный `opencode.json` — не локальная настройка отдельного разработчика, а один из главных уровней repo-level truth. Хороший проектный конфиг задает как минимум четыре вещи: набор инструкций, ограничения на skills, правила работы встроенных primary agents и общую permission policy.

## Минимально полезный конфиг

```
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "AGENTS.md",
    "docs/specs/*.md"
  ]
}
```

## Зрелый конфиг из репозитория-примера

```
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "AGENTS.md",
    "docs/specs/*.md"
  ],
  "permission": {
    "skill": {
      "*": "deny",
      "delivery-planning": "allow",
      "requirements-spec": "allow",
      "dbt-modeling": "allow",
      "python-etl": "allow"
    }
  },
  "agent": {
    "build": {
      "permission": {
        "task": {
          "*": "deny",
          "project-manager": "allow",
          "system-analyst": "allow",
          "data-engineer": "allow"
        },
        "bash": {
          "*": "allow",
          "git push*": "ask",
          "docker compose down*": "ask",
          "rm -rf *": "ask"
        }
      }
    }
  }
}
```

## Почему `instructions` важнее, чем кажется

Не пытайтесь засунуть всё знание проекта в один большой `AGENTS.md`. Используйте `instructions` как механизм композиции. Тогда `AGENTS.md` остается главным контрактом, а спецификации подключаются отдельно.

## Разрешения: практическая политика

| Тип действий | Здоровый дефолт | Почему |
|-------------|-----------------|--------|
| Read/search инструменты | `allow` | Без этого analysis phase становится мучительно медленным |
| Обычные локальные правки | `allow` или agent-specific | Иначе build-mode вязнет на каждом изменении |
| Внешние или опасные bash-команды | `ask` / `deny` | Push, destructive cleanup требуют осторожности |
| Доступ к skills | Whitelist | Меньше риск загружать неподходящие навыки |

## Паттерн: широкие права, но страховка опасных границ

```
"bash": {
  "*": "allow",
  "git push*": "ask",
  "docker compose down*": "ask",
  "rm -rf *": "ask"
}
```

## Паттерн: ограничивать task routing

```
"task": {
  "*": "deny",
  "project-manager": "allow",
  "system-analyst": "allow",
  "data-engineer": "allow"
}
```

## Рекомендуемые defaults для команды

- Всегда указывать `$schema`
- Подключать `AGENTS.md` и `docs/specs/*.md` через `instructions`
- Явно описывать whitelist для `permission.skill`
- Переопределять `agent.build.permission` хотя бы для опасных bash-patterns
- Использовать task permissions как механизм маршрутизации

## Чего не стоит класть в project config

- **Секреты:** не храните API keys в `opencode.json`
- **Всё знание в одном JSON:** конфиг должен оркестрировать, а не заменять docs и правила
