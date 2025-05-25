from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Udemy Clone Lite"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str
    BACKEND_CORS_ORIGINS: list[str] = []

    FIRST_SUPERUSER: str
    FIRST_SUPERUSER_PASSWORD: str

    ENVIRONMENT: str = "development"

    # ✅ v2 スタイル
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()  # ← 他モジュールから import して使う

