from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    OPENAI_API_KEY: str
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()