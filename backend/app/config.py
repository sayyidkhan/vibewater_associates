from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "vibewater_db"
    openai_api_key: str = ""
    coingecko_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
    
    def get_cors_origins_list(self) -> List[str]:
        """Convert cors_origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
