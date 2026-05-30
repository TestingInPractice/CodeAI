# MCP и интеграции

**Глава 06**

---

## Что такое MCP

Model Context Protocol (MCP) — открытый стандарт для подключения AI-приложений к внешним системам. После добавления MCP-сервера его инструменты становятся доступны LLM рядом со встроенными инструментами OpenCode.

## Когда MCP полезен

- Нужно подключать внешнюю документацию или knowledge base
- Нужно анализировать ошибки в observability-системе
- Нужно доставать информацию из удаленных систем
- Нужно дать агенту actions за пределами репозитория

## Главное ограничение: MCP расходует контекст

Подключайте только те серверы, которые реально дают выгоду в конкретном проекте.

## Как подключаются MCP-серверы

```
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "name-of-mcp-server": {
      "enabled": true
    }
  }
}
```

### Локальные MCP-серверы

```
{
  "mcp": {
    "my-local-mcp": {
      "type": "local",
      "command": ["npx", "-y", "my-mcp-command"],
      "enabled": true,
      "environment": {
        "MY_ENV_VAR": "value"
      }
    }
  }
}
```

### Удаленные MCP-серверы

```
{
  "mcp": {
    "my-remote-mcp": {
      "type": "remote",
      "url": "https://my-mcp-server.com",
      "enabled": true,
      "headers": {
        "Authorization": "Bearer {env:MY_API_KEY}"
      }
    }
  }
}
```

## OAuth в OpenCode MCP

```
opencode mcp auth my-oauth-server
opencode mcp list
opencode mcp logout my-oauth-server
```

## Как управлять MCP без перегрузки проекта

Отключайте MCP глобально и включайте только в нужных агентах:

```
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "enabled": true
    }
  },
  "tools": {
    "context7*": false
  },
  "agent": {
    "system-analyst": {
      "tools": {
        "context7*": true
      }
    }
  }
}
```

## Практические MCP-сценарии

| Сценарий | MCP | Зачем |
|----------|-----|-------|
| Поиск документации библиотек | Context7 | Свежие примеры и docs |
| Разбор production errors | Sentry MCP | Доступ к проблемам и stack traces |
| Поиск open-source решений | Grep by Vercel | Внешние кодовые примеры |

## MCP, пользовательские инструменты и skills: не перепутать

- **MCP** — внешние системы через стандартный протокол
- **Пользовательские инструменты** — ваши JS/TS-инструменты внутри OpenCode
- **Skills** — инструкции и playbooks, не инструменты

Начинайте с малого: один-два полезных MCP-сервера, а не «зоопарк интеграций».
