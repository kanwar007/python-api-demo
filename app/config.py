from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Python REST API"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_bytes: int = 5242880
    log_backup_count: int = 3
    database_path: str = "data/app.db"
    auth_username: str = ""
    auth_password: SecretStr = SecretStr("")
    jwt_secret: SecretStr = SecretStr("")
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()