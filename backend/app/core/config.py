from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Invito"
    ENV: str = "development"
    VERSION: str = "1.0.0"

    DATABASE_URL: str

    class Config:
        env_file = ".env"


settings = Settings()