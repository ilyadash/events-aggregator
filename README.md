# Events Aggregator

REST API сервис-агрегатор для работы с мероприятиями — промежуточный слой между клиентами и внешним Events Provider API. Добавляет фоновую синхронизацию, удобную пагинацию, фильтрацию по дате, кэширование мест и валидацию данных.

## Возможности

- **Фоновая синхронизация** — ежедневная инкрементальная синхронизация событий из внешнего API через APScheduler + ручной триггер
- **Список событий** — пагинация (`page`/`page_size`) и фильтрация по дате из локальной БД
- **Детальная информация** — событие, площадка проведения, схема мест (`seats_pattern`)
- **Свободные места** — получение из внешнего API с in-memory кэшированием (30 секунд)
- **Регистрация и отмена** — создание/удаление билетов с валидацией статуса события и доступности места

## Технологический стек

| Категория | Инструмент |
|---|---|
| API | FastAPI (Python 3.12) |
| База данных | PostgreSQL 16 + SQLAlchemy (async) + asyncpg |
| Миграции | Alembic |
| Фоновые задачи | APScheduler |
| HTTP-клиент | httpx |
| Валидация | Pydantic / pydantic-settings |
| Менеджер пакетов | uv |
| Линтер | ruff |
| Контейнеризация | Docker + docker compose |
| CI/CD | GitHub Actions |

## Структура проекта

```
app/
├── api/routes/          # HTTP-слой (health, events, tickets, sync)
├── usecases/            # Бизнес-логика (Repository + UseCase)
├── repositories/        # Доступ к данным (EventRepository, TicketRepository, SyncRepository)
├── services/            # Интеграции (EventsProviderClient, EventsPaginator, sync_service)
├── models/              # ORM-модели SQLAlchemy (Event, Place, Registration, SyncMetadata)
├── schemas/             # Pydantic-схемы ответов и запросов
├── utils/               # Утилиты (парсер схемы мест)
├── config.py            # Настройки через переменные окружения
├── database.py          # Асинхронный движок SQLAlchemy
├── deps.py              # Dependency Injection (FastAPI Depends)
├── main.py              # Точка входа FastAPI
└── scheduler.py         # APScheduler (cron-задачи)

tests/
├── unit/                # Юнит-тесты (pytest + unittest.mock + respx)
├── integration/         # Интеграционные тесты (testcontainers + PostgreSQL)
└── conftest.py          # Общие фикстуры

alembic/                 # Миграции схемы БД
docs/                    # Документация Events Provider API
```

## Архитектура

Проект следует принципам чистой архитектуры с чётким разделением ответственности:

```
HTTP-слой (routes) → Бизнес-логика (usecases) → Доступ к данным (repositories) / Интеграции (services)
```

- **Routes** — только получают зависимости и вызывают `uc.do()`, не содержат логики
- **Use Cases** — принимают репозитории и клиенты через конструктор, не знают ни о HTTP, ни о БД напрямую
- **Repositories** — инкапсулируют SQL-запросы, возвращают ORM-модели
- **Services** — `EventsProviderClient` (HTTP-клиент к внешнему API) и `EventsPaginator` (асинхронный итератор cursor-based пагинации)

## API Endpoints

| Метод | URL | Описание |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/sync/trigger` | Ручной запуск синхронизации |
| `GET` | `/api/events` | Список событий с пагинацией и фильтрацией |
| `GET` | `/api/events/{event_id}` | Детали события |
| `GET` | `/api/events/{event_id}/seats` | Свободные места |
| `POST` | `/api/tickets` | Регистрация на событие |
| `DELETE` | `/api/tickets/{ticket_id}` | Отмена регистрации |

### Примеры

**Получение списка событий:**

```bash
curl -X GET "http://localhost:8000/api/events?date_from=2026-01-01&page=1&page_size=20"
```

**Регистрация на событие:**

```bash
curl -X POST "http://localhost:8000/api/tickets" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "email": "ivan@example.com",
    "seat": "A15"
  }'
```

**Запуск синхронизации:**

```bash
curl -X POST "http://localhost:8000/api/sync/trigger"
```

## Переменные окружения

Настраиваются через `.env` файл или переменные окружения контейнера:

| Переменная | По умолчанию | Описание |
|---|---|---|
| `POSTGRES_USERNAME` | `postgres_user` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | `postgres_pass` | Пароль PostgreSQL |
| `POSTGRES_HOST` | `localhost` | Хост PostgreSQL |
| `POSTGRES_PORT` | `5432` | Порт PostgreSQL |
| `POSTGRES_DATABASE_NAME` | `aggregator_db` | Имя БД |
| `POSTGRES_CONNECTION_STRING` | (пусто) | Полный DSN (переопределяет отдельные параметры) |
| `EVENT_PROVIDER_URL` | (пусто) | URL внешнего Events Provider API |
| `LMS_API_KEY` | (пусто) | API-ключ для доступа к Events Provider |
| `SYNC_CRON` | `0 3 * * *` | Cron-расписание фоновой синхронизации |
| `PAGE_SIZE` | `20` | Размер страницы по умолчанию |
| `SEATS_CACHE_TTL` | `30` | TTL кэша свободных мест (секунды) |

Пример `.env` для локальной разработки:

```env
POSTGRES_HOST=db
POSTGRES_USERNAME=postgres_user
POSTGRES_PASSWORD=postgres_pass
POSTGRES_DATABASE_NAME=aggregator_db
POSTGRES_PORT=5432
EVENT_PROVIDER_URL=https://events-provider.example.com
LMS_API_KEY=your_api_key_here
```

## Быстрый старт

### Требования

- Docker и docker compose
- uv (для локальной разработки без Docker)
- Python 3.12+ (для локальной разработки без Docker)

### Локальная разработка (с Docker)

```bash
# Запуск в dev-режиме (с автообновлением при изменении кода)
cp .env.example .env
docker compose --profile dev watch

# Запуск в production-режиме
docker compose --profile production up -d
```

### Локальная разработка (без Docker)

```bash
# Установка зависимостей
uv sync

# Миграции БД
uv run alembic upgrade head

# Первичная синхронизация событий
uv run python -c "import asyncio; from app.services.sync_service import sync_all; asyncio.run(sync_all())"

# Запуск сервера
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Запуск тестов

```bash
# Юнит-тесты (не требуют БД)
uv run pytest tests/unit/

# Все тесты (включая интеграционные — требуют Docker)
uv run pytest
```

### Проверка линтером

```bash
uv run ruff check .
```

## CI/CD

GitHub Actions пайплайн (`.github/workflows/ci.yml`):

```
lint (ruff) → test (pytest) → build (Docker multi-arch) → deploy
```

- **Lint** — проверка ruff (PEP8) перед всеми остальными шагами
- **Test** — unit + integration тесты с PostgreSQL service container
- **Build** — мультиархитектурная сборка Docker-образа (`linux/amd64`, `linux/arm64`) и push в GHCR
- **Deploy** — отправка запроса на развёртывание в Kubernetes-кластер
