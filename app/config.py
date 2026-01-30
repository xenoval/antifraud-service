from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    cache_ttl: int = 3600
    
    # Приложение
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = False
    
    # Логирование
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()