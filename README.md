# Notes App (FastAPI + SQLAlchemy + Postgres + Alembic)

Учебное приложение для заметок с HTML-интерфейсом и JSON API.

Функциональность:
- список заметок
- создание, редактирование, удаление
- валидация данных
- Postgres + миграции

---

## Стек

- Python 3.9+
- FastAPI
- SQLAlchemy 2.0 (sync)
- Postgres (Docker Compose)
- Alembic
- Uvicorn

---

## Требования

- Python 3.9+
- Docker Desktop
- macOS / Linux

---

## Установка и запуск (локально)

### 1. Клонировать репозиторий

```bash
git clone <REPO_URL>
cd notes-app
```

### 2. Создать и активировать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## Конфигурация

Приложение использует переменные окружения.

### `.env` файл (локально)

Создайте файл `.env` в корне проекта (он не коммитится):

```env
DATABASE_URL=postgresql+psycopg://notes:notes@localhost:5432/notes
```

---

## Запуск Postgres

Поднять базу данных:

```bash
docker compose up -d
```

Проверить статус:

```bash
docker compose ps
```

Остановить:

```bash
docker compose down
```

---

## Миграции (Alembic)

Перед запуском приложения примените миграции:

```bash
alembic upgrade head
```

Создание новой миграции при изменении моделей:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

---

## Запуск приложения

```bash
uvicorn main:app --reload
```

Открыть в браузере:
- HTML UI: http://127.0.0.1:8000/
- Swagger (API): http://127.0.0.1:8000/docs
- SQLAdmin: http://127.0.0.1:8000/admin

---

## API

- `GET /notes` — список заметок
- `POST /notes` — создать заметку
- `PUT /notes/{id}` — обновить заметку
- `DELETE /notes/{id}` — удалить заметку

---

## Частые проблемы

### Ошибка подключения к БД
Проверьте:
- контейнер Postgres запущен (`docker compose ps`)
- переменная `DATABASE_URL` задана
- миграции применены (`alembic upgrade head`)

---

## Статус
Учебный проект.
