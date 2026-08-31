from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ChargeGuard AI"
    database_url: str = "sqlite:///./chargeguard.db"
    razorpay_key_id: str = "test_key"
    razorpay_key_secret: str = "test_secret"
    ollama_base_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()