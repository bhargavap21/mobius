"""Configuration management using environment variables"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # AI API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Trading API Keys (Alpaca)
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "")
    alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "")
    alpaca_base_url: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

    # Social Media APIs
    reddit_client_id: str = os.getenv("REDDIT_CLIENT_ID", "")
    reddit_client_secret: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    reddit_user_agent: str = os.getenv("REDDIT_USER_AGENT", "TradingBot/1.0")

    # Twitter API
    twitter_bearer_token: str = os.getenv("TWITTER_BEARER_TOKEN", "")

    # News API
    news_api_key: str = os.getenv("NEWS_API_KEY", "")

    # Historical Sentiment APIs
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")
    quiver_api_key: str = os.getenv("QUIVER_API_KEY", "")
    polygon_api_key: str = os.getenv("POLYGON_API_KEY", "")
    iex_api_key: str = os.getenv("IEX_API_KEY", "")

    # Application Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Supabase Settings
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_anon_key: str = os.getenv("SUPABASE_ANON_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
