"""
Configuration module for the API service.

Responsibilities:
- Load environment variables
- Provide typed configuration access
- Centralize service configuration

Future configuration:
- database connection
- redis connection
- model provider configuration
- observability endpoints
"""

import os
ENV = os.getenv("ENV", "local")

# Load .env.local ONLY in local environment
if ENV == "local":
    try:
        from dotenv import load_dotenv
        load_dotenv(".env.local", override=False)
        load_dotenv(".env.secrets", override=False)
    except Exception:
        # Fail silently — local dev convenience only
        pass
    
class Settings:
    APP_NAME = os.getenv("APP_NAME", "b2b-ai-saas-infra-blueprint")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    REDIS_URL = os.getenv("REDIS_URL", "")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gtp-4.1-mini")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

settings = Settings()