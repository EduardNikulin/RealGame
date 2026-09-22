# План проекта: Платформа городских квестов (RealGame)

Архитектура проекта представляет собой monorepo, разделенное на бэкенд (FastAPI) и фронтенд (React).

## Технологический стек
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy ORM, Alembic (миграции), PostgreSQL, Pydantic, PyJWT, Passlib (bcrypt)
- **Frontend:** Node.js, React, React Router DOM, React Context API, Axios, Leaflet.js / React-Leaflet

## Быстрый старт для локальной разработки

### Настройка бэкенда
1. Перейти в папку `backend`.
2. Создать виртуальное окружение: `python -m venv venv`
0. ? Обновить пип: python -m pip install --upgrade pip
3. Активировать окружение и установить зависимости: `pip install -r requirements.txt`
4. Выполнить миграции базы данных через Alembic: `alembic upgrade head`
5. Запустить сервер FastAPI: `uvicorn app.main:app --reload`

### Настройка фронтенда
1. Перейти в папку `frontend`.
2. Установить зависимости: `npm install`
3. Запустить сервер разработки Vite: `npm run dev`
4. Интерактивная карта настраивается с использованием библиотек Leaflet.js и React-Leaflet.

### Тон коммитов:
feat: — добавление нового функционала (например, feat: add user authentication).
fix: — исправление ошибки/бага (например, fix: correct validation radius for GPS).
docs: — изменения исключительно в документации (например, docs: update README).
style: — правка форматирования, отступов, пропущенных точек с запятой (без изменения логики кода).
refactor: — переписывание кода без изменения его поведения (улучшение структуры, чистота кода).
chore: — рутинные задачи, обновление зависимостей в requirements.txt, конфигурация инструментов.