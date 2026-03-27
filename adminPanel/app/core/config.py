from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pricing.db"
    secret_key: str = "dev-secret-key"

    class Config:
        env_file = ".env"


settings = Settings()