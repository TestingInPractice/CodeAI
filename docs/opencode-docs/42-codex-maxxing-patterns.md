# Codex-maxxing — паттерны для OpenCode

> **Источник:** https://jxnl.github.io/blog/writing/2026/05/10/codex-maxxing/  
> **Автор:** Jason Liu

Выжимка практик, которые работают не только в Codex, но и в OpenCode.

---

## 1. Obsidian vault как постоянная память агента

Самый важный паттерн. Агент живёт **в Obsidian vault**, а не в репозитории. Репозитории — для кода. Vault — для контекста: люди, решения, открытые вопросы, заметки по проектам.

```
vault/
├── AGENTS.md              ← инструкции: обновляй vault по мере работы
├── TODO.md
├── people/                ← заметки о людях
├── projects/              ← статусы проектов
├── agent/                 ← память агента
└── notes/                 ← ежедневные заметки
```

### AGENTS.md для vault

```markdown
# AGENTS.md — корень Obsidian vault
As you learn more about people, make progress on projects,
or close an open loop, update the relevant pages in the vault.

- When you learn something about a person, update people/<name>.md
- When a project status changes, update projects/<name>.md
- When a decision is made, log it in notes/decisions.md
- Close loops in TODO.md when resolved
```

### Vault как GitHub repo

```bash
git init vault && cd vault
git remote add origin https://github.com/you/vault.git
git push -u origin main
```

Это даёт **diff как surface для ревью памяти**. Когда агент обновил vault, читаешь diff — видишь что он посчитал важным запомнить.

### В связке с OHS

Vault + OHS (Obsidian Hybrid Search) как MCP-сервер даёт семантический поиск по всей памяти агента. См. `docs/opencode-docs/obsidian/36-obsidian-hybrid-search-ohs.md`.

---

## 2. Durable threads — долгоживущие треды по workstream'ам

Не начинай новый чат на каждую задачу. Заведи **pinned thread на каждый workstream** и компактируй его неделями/месяцами.

Примеры постоянных тредов:
-   Chief of Staff (координация)
-   Проект X (разработка)
-   Twitter/Slack мониторинг
-   Архитектурные решения

Тред накапливает историю, предпочтения, прошлые решения. Не нужно переобъяснять контекст каждый раз.

**Tradeoff:** длинные треды дороже (кеш протухает). Окупается для важных workstream'ов, где continuity важнее стоимости.

---

## 3. Voice input — диктовка неотредактированных мыслей

Ценность не в скорости, а в **сырости**. Сказать «там какой-то Ben в Slack упоминал, я не помню точно, просто посмотри» — слишком размыто чтобы печатать, но естественно для голоса.

То же с транскриптами звонков: записал разговор (через Granola или аналоги), скормил агенту как стартовый материал. Планы получаются лучше, когда у модели есть «грязная» версия мысли, а не только отполированная.

---

## 4. Goals с верификацией

Слабый goal: «реализуй план из этого Markdown-файла».  
Сильный goal: **реальный критерий успеха**, который агент может проверить.

Пример Jason: портировать Python-библиотеку Rich в Rust — **но пройти все unit-тесты оригинальной библиотеки**.

Формула: `Goal = амбициозная цель + верификация (тесты, diff, метрики)`.

Без верификации goal — просто wish.

---

## 5. Непрерывные циклы (аналог Heartbeats)

Codex имеет встроенные Heartbeats. В OpenCode это можно сделать через:

- **MCP-сервер** с планировщиком, который дёргает агента по расписанию
- **GitHub Actions / cron** — запуск `opencode run` по расписанию
- **Внешний мониторинг** — CI/CD триггерит агента при изменениях

Пример цикла «Chief of Staff»:
```
Каждые N минут:
  1. Проверить Slack/Gmail на непрочитанные сообщения
  2. Если вопрос — исследовать и подготовить ответ
  3. Обновить vault с результатами
  4. Не отправлять без подтверждения
```

---

## Итог: рабочая схема для OpenCode

```
Obsidian vault (AGENTS.md + память агента)
    ↕ через OHS MCP
OpenCode (durable threads по workstream'ам)
    ↕ через opencode.json instructions
Код в репозиториях + верификация (test suite)
```

- Vault хранит контекст, который переживает треды
- AGENTS.md в vault говорит агенту как вести vault
- OpenCode thread — текущая сессия с историей
- Goals с тестами — критерий «сделано»
