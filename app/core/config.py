from functools import lru_cache
from typing import List
import json
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg://hub:hubpass@localhost:5433/hubdb_v2"

    # Auth
    JWT_SECRET: str = "change-this-in-production"
    ACCESS_TOKEN_EXPIRES_MIN: int = 30
    REFRESH_TOKEN_EXPIRES_MIN: int = 43200  # 30 days

    # Feature flags
    ENABLE_PREFLIGHT: bool = True
    ENABLE_BOOTSTRAP: bool = True
    ENABLE_DB_INIT_CHECK: bool = True
    ALLOW_AUTO_DB_INIT: bool = True
    CREATE_DEFAULT_ADMIN: bool = True

    DEFAULT_ADMIN_EMAIL: str = "admin@internhub.local"
    DEFAULT_ADMIN_PASSWORD: str = "ChangeMe123!"

    LAZY_LOADING: bool = True
    STATELESS_STRICT: bool = True
    ALLOW_REFRESH_TOKEN_STORE: bool = False

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except (json.JSONDecodeError, ValueError):
                # If not JSON, split by comma
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


def get_settings() -> Settings:
    settings = Settings()
    # Debug: Print CORS origins to verify parsing
    print(f"🔧 Settings loaded - CORS_ORIGINS: {settings.CORS_ORIGINS} (type: {type(settings.CORS_ORIGINS)})")
    if isinstance(settings.CORS_ORIGINS, list):
        print(f"   ✅ CORS_ORIGINS is a list with {len(settings.CORS_ORIGINS)} items")
        for i, origin in enumerate(settings.CORS_ORIGINS):
            print(f"      [{i}] {origin}")
    else:
        print(f"   ❌ WARNING: CORS_ORIGINS is NOT a list! It's: {type(settings.CORS_ORIGINS)}")
    return settings


# Use function call instead of cached to allow reloading
settings = get_settings()


