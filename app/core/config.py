from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URL: str = os.environ.get("MONGODB_URL")
    MONGODB_DB_NAME: str = os.environ.get("MONGODB_DB_NAME")
    CLOUDINARY_SECRET: str = os.environ.get("CLOUDINARY_SECRET")
    MISTRAL_API_KEY: str = os.environ.get("MISTRAL_API_KEY")    

    class Config:
        env_file = ".env"

settings = Settings()