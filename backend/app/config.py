from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str = ""  # Supabase PostgreSQL connection string
    openai_api_key: str = ""
    coingecko_api_key: str = ""
    cors_origins: str = "http://localhost:3000"
    
    # AWS Bedrock settings
    aws_bearer_token_bedrock: str = ""
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
    aws_model_id: str = ""  # Alternative field name for compatibility
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields from .env
    
    def get_cors_origins_list(self) -> List[str]:
        """Convert cors_origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
