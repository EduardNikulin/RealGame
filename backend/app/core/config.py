from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Указываем переменные и их типы данных
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  # Здесь можно сразу задать значение по умолчанию

    # Настройка Pydantic для чтения .env файла
    model_config = SettingsConfigDict(
        env_file=".env",           # Имя файла, откуда брать переменные
        env_file_encoding="utf-8", # Кодировка файла
        extra="ignore"             # Игнорировать другие переменные в окружении, если они есть
    )

# Создаем один экземпляр настроек для использования во всем проекте
settings = Settings()
