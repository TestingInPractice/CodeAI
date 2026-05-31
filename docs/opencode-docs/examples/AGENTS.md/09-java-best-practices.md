# AGENTS.md для Java-разработчика

## Build & Test
- Build: `mvn clean compile` / `mvn clean install -DskipTests`
- Test: `mvn test` / `mvn verify`
- Single test: `mvn test -Dtest=ClassName#methodName`
- Skip slow tests: `mvn test -DexcludedGroups=integration`
- Code quality: `mvn verify -Psonar` (Sonar gate обязателен перед merge)

## Code Style
- Обработка исключений: **не игнорируй**. Всегда думай что нужно тому, кто будет дебажить
- Unchecked exceptions (RuntimeException) предпочтительнее checked — Spring и современные фреймворки их не любят
- Минимальная область видимости переменных: объявляй в самом узком блоке где нужна
- String concat в циклах — не используй `+`, используй `StringBuilder`
- ENUM'ы читаемее констант — используй их
- Immutability: минимизируй мутабельность, `final`-поля по умолчанию
- Маркерные интерфейсы — используй когда нужно пометить класс семантически (как `Serializable`)
- Floats для расчётов — не используй, BigDecimal вместо них
- Builder — для сложных объектов (больше 3-4 полей или обязательные+опциональные)

## Architecture
- Слои: Web Layer → Service Layer → Business Layer → Data Layer
- Service layer — фасад для бизнес-логики, граница транзакций
- REST API: HTTP-статусы, единый формат ошибок, JAXB/JAX-RS или Spring MVC
- Микросервисы: каждый сервис — свой репозиторий, своя БД, своя CI/CD pipeline
- Всегда используй Continuous Integration с первого дня
- Logging + correlation ID + centralized monitoring — обязательно
- Нет циклических зависимостей между модулями

## Design Principles
- SOLID — это минимум
- 4 принципа простого дизайна (по важности):
  1. Все тесты проходят
  2. Минимум дублирования
  3. Максимум ясности
  4. Всё маленькое (методы, классы, компоненты)
- Компоненты маленькие, с одной ответственностью
- Dependency Injection через конструктор, не через field injection

## Testing
- Unit тесты обязательны для всей бизнес-логики
- Mockito для внешних зависимостей
- TDD: пиши тест → код → рефактори
- BDD (Cucumber/Fitnesse) — для коммуникации между аналитиками и разработчиками
- Code coverage ≠ качество — не гонись за процентом, проверяй логику
- Производительность тестов важна: быстрые — в pre-commit hook, медленные — в nightly build

## NFRs
- Performance, Scalability, Maintainability, Portability, Availability, Security, Testability
- Кэширование на уровне бизнес-логики (не на веб-слое)
- Stateless приложения масштабируются лучше
- Безопасность: валидация на границе (вход/выход сервиса)

## Maven
- Родительский POM для общих зависимостей и плагинов
- `api` и `impl` в разных модулях для чётких границ
- Версии зависимостей — в parent POM, dependencyManagement
- В плагины заверни: compiler, surefire, failsafe, checkstyle, spotbugs, jacoco
