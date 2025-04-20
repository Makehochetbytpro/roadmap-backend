from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # Загружаем переменные окружения из .env

class Settings(BaseSettings):
<<<<<<< HEAD
=======
    database_url: str
>>>>>>> 2625b6ee368996f980b842d7467fec4980eddfe2
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()

