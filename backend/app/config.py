import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./db/questions.db")
    CSV_PATH: str = os.getenv("CSV_PATH", "questions.csv" if os.path.exists("questions.csv") else "/mnt/data/questions.csv")

settings = Settings()
