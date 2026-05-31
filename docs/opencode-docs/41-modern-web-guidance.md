# Modern Web Guidance — как использовать в OpenCode

> **Сайт:** https://developer.chrome.com/docs/modern-web-guidance  
> **GitHub:** https://github.com/GoogleChrome/modern-web-guidance-src  
> **CLI:** `npx modern-web-guidance@latest`

Modern Web Guidance (MWG) от Chrome-команды — набор скиллов (100+ use cases) по современным веб-стандартам: CSS Container Queries, Popover API, View Transitions, INP-диагностика, passkeys, Baseline-совместимость и т.д.

---

## Установка

```bash
npx modern-web-guidance@latest install
```

С CLI-установка: скиллы копируются в `~/.claude/skills/` — OpenCode их подхватит автоматически (если не отключён `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS`).

---

## Использование в AGENTS.md

Достаточно указать Baseline target. MWG сам решит какие фичи предлагать.

```markdown
# AGENTS.md
This project's Baseline target is Baseline 2024.
```

Без настройки — `Baseline Widely available` (самый консервативный).

---

## Поиск нужного гайда

```bash
# Найти use case по описанию
npx modern-web-guidance@latest search "animate dialog modal backdrop"

# Получить полный гайд по ID
npx modern-web-guidance@latest retrieve "animate-to-from-top-layer"
```

Вывод — plain markdown, можно скопировать или передать агенту через `instructions`.

---

## Если CLI не подходит — `instructions` в opencode.json

MWG — это просто markdown-файлы на GitHub. Можно ссылаться напрямую:

```json
{
  "instructions": [
    "https://raw.githubusercontent.com/GoogleChrome/modern-web-guidance-src/main/guides/user-experience/animate-to-from-top-layer/guide.md",
    "https://raw.githubusercontent.com/GoogleChrome/modern-web-guidance-src/main/guides/css/container-queries/guide.md"
  ]
}
```

---

## Пример промпта для OpenCode

После установки скиллов и настройки Baseline:

```
Create an accordion-style stats component that smoothly animates on open and close.
Use modern CSS features appropriate for Baseline 2024.
```

MWG-скилл перехватит запрос и подставит актуальные гайды.

---

## Как это работает

```
Запрос пользователя
  → OpenCode читает AGENTS.md (Baseline target)
  → MWG skill определяет релевантный use case
  → CLI `modern-web-guidance search/retrieve`
  → Агент получает гайд с современным API + fallback
  → Результат: код на современном стеке, а не jQuery/CJS
```

По данным Google: +37 п.п. к adherence to modern best practices против неассистированного агента.
