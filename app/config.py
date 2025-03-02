from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    RATE_LIMIT_MINUTE: int = 20
    RATE_LIMIT_DAY: int = 5000
    IMAGES_COLLECTION: str
    REDIS_URL: str = "redis://localhost:6379"
    CDN_DOMAIN: str
    STATIC_IMAGES_DIR: str = "static/images"
    API_KEYS_COLLECTION: str

    # Configuration for pydantic-settings: load environment variables from .env.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instantiate the settings so that they can be imported throughout the app.
settings = Settings()