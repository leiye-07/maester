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

class Settings:
    APP_NAME = os.getenv("APP_NAME", "b2b-ai-saas-infra-blueprint")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    REDIS_URL = os.getenv("REDIS_URL", "")

settings = Settings()