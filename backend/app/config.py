import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./backend/db/questions.db" if os.path.exists("backend/db") else "sqlite:///./db/questions.db")
    CSV_PATH: str = os.getenv("CSV_PATH", "backend/question.csv" if os.path.exists("backend/question.csv") else "question.csv")

settings = Settings()
