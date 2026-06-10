# browse.sh — Browser CLI и каталог веб-скиллов для агентов

**Сайт:** https://browse.sh

---

## Что это

**browse.sh** — CLI-инструмент и каталог готовых навыков для браузерной автоматизации через AI-агентов. Позволяет агенту управлять браузером и выполнять действия на веб-сайтах без необходимости писать код автоматизации вручную.

---

## Установка

```bash
npm install -g browse
```

---

## CLI возможности

- **Установка навыков** — `browse install <skill>` для доменной браузерной автоматизации
- **Browser primitives** — click, scroll, type, hover, press
- **Network/console tail** — отладка сетевых запросов и консоли браузера
- **Cloud sessions** — `browse cloud` для Browserbase cloud сессий
- **Локальный запуск** — без облака

---

## Agent Surfaces (для обнаружения агентами)

| Поверхность | URL | Описание |
|-------------|-----|----------|
| llms.txt | https://browse.sh/llms.txt | Компактный индекс для agent discovery |
| llms-full.txt | https://browse.sh/llms-full.txt | Полный каталог с содержимым всех SKILL.md |
| Skill catalog | https://browse.sh/ | Человеческий UI для просмотра навыков |

---

## Каталог навыков (примеры)

На сайте доступны **сотни skills** для конкретных сайтов и задач:

**Покупки:** Amazon, eBay, Etsy, Walmart, Best Buy, Home Depot, IKEA, Instacart, DoorDash  
**Путешествия:** Airbnb, Booking.com, Kayak, Google Flights, OpenTable, HotPads, Realtor.com  
**Поиск работы:** LinkedIn Jobs, Indeed  
**Транспорт:** FedEx, UPS, CarGurus, Hertz, Avis  
**Развлечения:** Ticketmaster, IMDB, Goodreads, Discogs, Heritage Auctions  
**Госуслуги:** IRS, Medicare, Healthcare.gov, CA DMV  
**И многое другое** — сотни готовых сценариев

---

## Как работает

1. Устанавливаешь `browse` CLI
2. Агент (Claude Code, OpenCode) автоматически обнаруживает browse.sh через `llms.txt`
3. Агент выбирает подходящий skill из каталога под задачу пользователя
4. Skill содержит готовый сценарий: URL, параметры, ожидаемый формат ответа
5. Агент выполняет skill через browse CLI — кликает, скроллит, читает данные
6. Результат возвращается агенту в структурированном JSON/Markdown

---

## Отличие от обычного browser automation

- **Не нужно писать Playwright/Puppeteer** — готовые skills для каждого сайта
- **Обход антибот-защиты** — встроенный Browserbase stealth
- **Read-only по умолчанию** — навыки не совершают покупки/бронирования без подтверждения
- **Agent-native** — навыки заточены под то, как AI-агенты читают и принимают решения

---

## Отношение к нашему проекту

browse.sh — это источник **готовых браузерных skills**, которые можно использовать в CodeAI Build Loop для задач, требующих веб-автоматизации (проверка цен, мониторинг, сбор данных). Аналог OpenCode skills, но для веб-автоматизации.

---

**↪️ Категория:** [[README]]
