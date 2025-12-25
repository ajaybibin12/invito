from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Invito"
    ENV: str = "development"
    VERSION: str = "1.0.0"

    DATABASE_URL: str
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None
    ADMIN_ROLE: str = "admin"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SECRET_KEY: str 

    class Config:
        env_file = ".env"


settings = Settings()