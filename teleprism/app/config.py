"""Application settings."""

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-backed settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    bot_token: str = ""
    bot_username: str = ""
    owner_ids: list[int] = Field(default_factory=list)
    manager_chat_id: int = 0
    database_path: Path = Path("./data/teleprism.sqlite3")
    backup_directory: Path = Path("./data/backups")
    backup_retention_days: int = 14
    payments_provider: str = "cryptapi"  # cryptapi | mock
    mock_confirm_seconds: int = 20
    cryptapi_ticker: str = "trc20/usdt"
    cryptapi_wallet_address: str = ""
    cryptapi_callback_sink: str = ""
    cryptapi_confirmations: int = 1
    payment_ttl_minutes: int = 30
    payment_grace_period_hours: int = 24
    payment_poll_initial_interval: int = 10
    payment_poll_normal_interval: int = 20
    payment_poll_expired_interval: int = 120
    payment_poll_concurrency: int = 5
    min_stars: int = 50
    max_stars: int = 10_000
    custom_stars_step: int = 50
    manager_sla_warning_minutes: int = 5
    manager_sla_admin_minutes: int = 15
    manager_processing_timeout_minutes: int = 30
    require_manager_proof: bool = False
    raito_hot_reload: bool = True
    raito_repl_enabled: bool = True
    log_level: str = "INFO"

    @field_validator("owner_ids", mode="before")
    @classmethod
    def parse_owner_ids(cls, value: object) -> list[int]:
        """Parse comma-separated owner IDs."""

        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [int(item) for item in value]
        return [int(part.strip()) for part in str(value).split(",") if part.strip()]


def load_settings() -> Settings:
    """Load application settings."""

    return Settings()
