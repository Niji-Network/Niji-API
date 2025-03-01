from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and a .env file.

    Attributes:
        MONGO_URI (str): MongoDB connection URI.
        DB_NAME (str): Name of the MongoDB database.
        RATE_LIMIT_MINUTE (int): Maximum allowed requests per minute.
        RATE_LIMIT_DAY (int): Maximum allowed requests per day.
        IMAGES_COLLECTION (str): Name of the MongoDB collection for images.
        ALLOWED_POST_USERS (List[str]): List of usernames allowed to post/update images.
        REDIS_URL (str): Redis connection URL used for rate limiting.
        CDN_DOMAIN (str): The CDN domain for serving images.
        STATIC_IMAGES_DIR (str): Relative directory where images are stored locally.
        API_KEYS_COLLECTION (str): Name of the MongoDB collection for API keys.
    """
    MONGO_URI: str
    DB_NAME: str
    RATE_LIMIT_MINUTE: int = 20
    RATE_LIMIT_DAY: int = 5000
    IMAGES_COLLECTION: str
    ALLOWED_POST_USERS: List[str] = ["gonzyui"]
    REDIS_URL: str = "redis://localhost:6379"
    CDN_DOMAIN: str
    STATIC_IMAGES_DIR: str = "static/images"
    API_KEYS_COLLECTION: str

    # Configuration for pydantic-settings: load environment variables from .env.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instantiate the settings so that they can be imported throughout the app.
settings = Settings()