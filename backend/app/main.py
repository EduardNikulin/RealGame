import os                                                                               # Для работы с путями папок
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles                                             # Модуль для раздачи статики
from app.api.v1.api import api_router

app = FastAPI(
    title="RealGame API",
    description="Бэкенд для игрового проекта RealGame",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ПОДКЛЮЧАЕМ РАЗДАЧУ СТАТИКИ: Связываем URL-путь /static с реальной папкой static на диске
UPLOAD_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)                                                  # Защита: создаем папку, если стерлась
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")                  # Теперь картинки открываются по ссылкам

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "working", "message": "Welcome to RealGame API!"}
