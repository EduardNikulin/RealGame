from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

# Инициализируем наше FastAPI приложение
app = FastAPI(
    title="RealGame API",
    description="Бэкенд для игрового проекта RealGame",
    version="1.0.0"
)

# Список адресов, с которых нашему бэкенду разрешено принимать запросы
# Сюда мы пишем адрес нашего фронтенда (например, http://localhost:3000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Подключаем CORS-прослойку (Middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Разрешаем запросы с указанных сайтов
    allow_credentials=True,           # Разрешаем отправку куки и токенов авторизации
    allow_methods=["*"],              # Разрешаем любые HTTP-методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],              # Разрешаем любые HTTP-заголовки
)

# ПОДКЛЮЧАЕМ РОУТЕР К ПРИЛОЖЕНИЮ С ОБЩИМ ПРЕФИКСОМ /api/v1
app.include_router(api_router, prefix="/api/v1")

# Простейший тестовый роут, чтобы проверить, что сервер вообще живой
@app.get("/")
def read_root():
    return {"status": "working", "message": "Welcome to RealGame API!"}
