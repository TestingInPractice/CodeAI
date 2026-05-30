# Разбор gist: AGENTS-by-Boris-Cherny — построчное объяснение

> Оригинал: https://gist.github.com/orangeRat/64eb52352a86ef187bc4bf9e5a855fc4  
> Автор: Boris Cherny  
> Формат: AGENTS.md — работает в OpenCode, Cursor, Codex и других агентах

---

## Workflow Orchestration

### 1. Plan Node Default

```
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
```
Агент должен **включать plan mode** для любой нетривиальной задачи. Без этой строки агент может сразу начать писать код. С ней — сначала составит план. Порог: 3+ шага или архитектурные решения.

```
- If something goes sideways, STOP and re-plan immediately – don't keep pushing
```
Запрещает «героический» продалбливание в неправильном направлении. Если план сломался → стоп → новый план. Без этого агент может пытаться чинить сломанный план всё глубже.

```
- Use plan mode for verification steps, not just building
```
Plan mode не только для написания кода, но и для **проверки** результатов. Типичная ошибка агентов: написали код, сказали «готово», но не проверили.

```
- Write detailed specs upfront to reduce ambiguity
```
Перед реализацией — пиши spec. Это снижает неоднозначность, которую агент сам же создаст, если начнёт кодить без плана.

### 2. Subagent Strategy

```
- Use subagents liberally to keep main context window clean
```
Основной контекст — чистый, subagents делают чёрную работу. Без этой строки агент всё делает в основном окне и быстро съедает контекст.

```
- Offload research, exploration, and parallel analysis to subagents
```
Конкретно что отдавать subagent'ам: исследование кода, изучение документации, параллельный анализ разных вариантов.

```
- For complex problems, throw more compute at it via subagents
```
Сложные задачи ≠ больше времени в основном окне. Параллелизация через subagents.

```
- One tack per subagent for focused execution
```
Один subagent — одна задача. Не нагружать одного subagent несколькими целями.

### 3. Self-Improvement Loop

```
- After ANY correction from the user: update tasks/lessons.md with the pattern
```
Главный механизм обучения. Агент **обязан** записывать каждое исправление. Без этого агент будет делать ту же ошибку повторно в следующем сеансе.

```
- Write rules for yourself that prevent the same mistake
```
Не просто записать ошибку, а сформулировать **правило**, которое её предотвратит.

```
- Ruthlessly iterate on these lessons until mistake rate drops
```
Агент должен сам следить за динамикой ошибок и добиваться их снижения.

```
- Review lessons at session start for relevant project
```
В начале каждого сеанса — читать `tasks/lessons.md`. Иначе уроки прошлого сеанса потеряны (контекст свежий каждый раз).

### 4. Verification Before Done

```
- Never mark a task complete without proving it works
```
Жёсткий запрет на «код написан → задача готова». Нужно доказать, что работает.

```
- Diff behavior between main and your changes when relevant
```
Конкретный метод проверки: сравни поведение с `main` (или базовой веткой). Полезно, когда изменения затрагивают существующую логику.

```
- Ask yourself: "Would a staff engineer approve this?"
```
Мысленный фильтр качества. Агент должен сам оценить свой код на уровне staff engineer, прежде чем отдать.

```
- Run tests, check logs, demonstrate correctness
```
Конкретные действия верификации: тесты, логи, демонстрация. Без этой строки «verify» может быть абстрактным.

### 5. Demand Elegance (Balanced)

```
- For non-trivial changes: pause and ask "is there a more elegant way?"
```
Принудительная пауза на рефлексию. Агенты склонны к первому рабочему решению, а не к лучшему.

```
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
```
Если решение feels hacky — **переделать** элегантно, используя всё что узнал за время работы. Мощный приём против технического долга.

```
- Skip this for simple, obvious fixes – don't over-engineer
```
Баланс: не применять «demand elegance» к тривиальным правкам (опечатки, переименования). Иначе агент будет бесконечно рефакторить.

```
- Challenge your own work before presenting it
```
Агент должен быть сам себе code reviewer.

### 6. Autonomous Bug Fixing

```
- When given a bug report: just fix it. Don't ask for hand-holding
```
Ключевое для продуктивности: баг-репорт → агент идёт и фиксит, **не задавая уточняющих вопросов**. Экономит тонну времени.

```
- Point at logs, errors, failing tests – then resolve them
```
Агент сам находит источник проблемы (логи, ошибки, тесты) и чинит. Не просит показать где.

```
- Zero context switching required from the user
```
Пользователь не должен переключать контекст, чтобы объяснять очевидное.

```
- Go fix failing CI tests without being told how
```
Частный случай: CI упал → агент идёт чинить сам, не спрашивая «что делать?».

---

## Task Management

```
1. Plan First: Write plan to tasks/todo.md with checkable items
```
Первый шаг любой задачи — создать/обновить `tasks/todo.md` с list of checkable items. Без этого агент может работать хаотично, без отслеживания прогресса.

```
2. Verify Plan: Check in before starting implementation
```
Показать план пользователю **до** начала реализации. Это даёт возможность скорректировать направление до того, как потрачены токены на код.

```
3. Track Progress: Mark items complete as you go
```
По мере выполнения — отмечать сделанные пункты. Позволяет и агенту, и пользователю видеть прогресс. Важно для длинных задач.

```
4. Explain Changes: High-level summary at each step
```
После каждого шага — краткое описание что сделано. Пользователь понимает ход мыслей агента и может вмешаться, если что-то пошло не так.

```
5. Document Results: Add review section to tasks/todo.md
```
В конце задачи — документировать результат в todo.md. Создаёт историю изменений для будущих сеансов.

```
6. Capture Lessons: Update tasks/lessons.md after corrections
```
После каждого исправления от пользователя — записать урок. Механизм долговременной памяти агента (единственный, если нет auto memory).

---

## Core Principles

```
Simplicity First: Make every change as simple as possible. Impact minimal code.
```
Главный фильтр при выборе решения: **самое простое**. Агенты склонны к over-engineering. Эта строка — якорь.

```
No Laziness: Find root causes. No temporary fixes. Senior developer standards.
```
Запрет на временные решения (quick fixes, TODOs, workarounds). Агент должен найти первопричину. Уровень — senior разработчик.

```
Minimal Impact: Changes should only touch what's necessary. Avoid introducing bugs.
```
Каждое изменение должно затрагивать **минимум кода**. Чем меньше затронуто, тем меньше шанс внести баги.

---

## AGENTS.md (план-чеклист методология)

```
Every plan for a new task must be delivered as highly detailed implementation
and execution guidelines in Markdown format.
```
План должен быть **детальным** — не абстрактным. Без этого агент пишет «implement feature X» и идёт в код без конкретики.

```
Plans are saved to docs/plans/<date-time>/plan-<feature-name>.md
and their corresponding checklists to docs/plans/<date-time>/checklist-<feature-name>.md
```
Чёткая структура хранения: `docs/plans/<дата>/`. Позволяет вернуться к плану в следующем сеансе. Дата в пути — уникальность и хронология.

```
Each plan must include:
- Full context of the task
- Step-by-step execution instructions
- Implementation specifics and nuances
```
План обязан содержать **контекст** (чтобы не пересказывать), **пошаговую инструкцию** (последовательность), **нюансы** (подводные камни, которые агент уже знает).

```
Each checklist must cover:
- A summary of what was implemented
- Detailed verification steps to confirm all implementation details
  are in place and consistent with the original plan and intent
```
Чеклист — не просто «проверить что работает», а верификация **каждого пункта плана**. Сверка с оригинальным замыслом — защита от расхождения плана и реализации.

```
If a plan spans multiple stages, create a separate plan and checklist file
per stage so they can be executed one at a time.
```
Модульность планов. Для больших задач — разбить на stage'и, каждый со своим планом и чеклистом. Предотвращает context overflow.

```
Each subsequent stage must reference and build on the previous one
to maintain consistent context throughout the implementation.
```
Каждый следующий stage должен ссылаться на предыдущий. Иначе агент в новом сеансе начнёт с нулевого контекста.

```
After completing each stage, run the /simplify skill to optimize the implementation,
then run the checklist to verify the results.
```
Финальный ритуал каждого stage: `/simplify` (упростить код) → чеклист (верификация). `/simplify` — это OpenCode skill, который рефакторит без изменения поведения.
