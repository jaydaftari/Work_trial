from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = "development"
    DATABASE_URL: str

    ALPHAVANTAGE_API_KEY: str
    FINNHUB_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
