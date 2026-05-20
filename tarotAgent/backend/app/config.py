import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Tarot Agent"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite+aiosqlite:///./tarot.db"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    LLM_PROVIDER: str = "deepseek"
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"

    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_MCH_KEY: str = ""

    ALIPAY_APP_ID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""

    READING_PRICE_CENTS: int = 990

    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_ENDPOINT: str = ""
    OSS_BUCKET_NAME: str = ""
    OSS_CDN_DOMAIN: str = ""

    STATIC_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    TEMPLATES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
