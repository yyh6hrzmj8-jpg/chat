# Chat Support Bot (Fullstack)

Проект для итоговой аттестации: **чат-бот поддержки**.

- Backend: **FastAPI + SQLAlchemy (async) + Alembic + JWT + pytest**
- Frontend: **старый интерфейс сохранён (верстка/стили)**, логика подключена к API через `fetch/async/await`.

## Быстрый старт

### 1) Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# применить миграции
alembic upgrade head

# запустить
uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

### 2) Frontend

Открой `frontend/index.html` через Live Server (VS Code) или любой локальный статический сервер.

> Важно: если открыть файл двойным кликом (file://), браузер может блокировать запросы к API.

## API

- `POST /auth/register`
- `POST /auth/login`
- `POST /chat/session`
- `POST /chat/message`
- `GET /chat/history/{session_id}`

## Тесты

```bash
cd backend
pytest -q
```
