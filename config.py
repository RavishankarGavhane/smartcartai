from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:Ravi%231234@localhost:5432/smartcartai")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "An311jLWh5BTpGjsIw7VfYZBTSxQTAvbMuw3mY4neRs")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))
    
    # App
    APP_NAME: str = os.getenv("APP_NAME", "SmartCartAI")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Email Configuration - Hostinger Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.hostinger.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    DISPLAY_EMAIL: str = os.getenv("DISPLAY_EMAIL", "info@keepactivepro.com")
    DISPLAY_NAME: str = os.getenv("DISPLAY_NAME", "SmartCartAI Support")
    WELCOME_EMAIL_FROM: str = os.getenv("WELCOME_EMAIL_FROM", f"SmartCartAI <info@keepactivepro.com>")
    ORDER_EMAIL_FROM: str = os.getenv("ORDER_EMAIL_FROM", f"SmartCartAI Orders <info@keepactivepro.com>")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@keepactivepro.com")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This tells Pydantic to ignore extra fields

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()