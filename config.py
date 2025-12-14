import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_HOST = os.getenv("DATABASE_HOST", "13.214.153.0")
    DATABASE_PORT = int(os.getenv("DATABASE_PORT", 5432))
    DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "PasswordDotaafdb")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "postgres")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    @property
    def database_url(self):
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

config = Config()

