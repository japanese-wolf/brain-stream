"""Configuration management for BrainStream."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_prefix="BRAINSTREAM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "BrainStream"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    # Server
    host: str = "127.0.0.1"
    port: int = 3000

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///~/.brainstream/brainstream.db",
        description="Database connection URL",
    )

    # Data directory
    data_dir: Path = Field(
        default=Path.home() / ".brainstream",
        description="Directory for storing application data",
    )

    # LLM
    llm_provider: Literal["claude", "copilot"] = "claude"
    llm_timeout: int = 120  # seconds

    def get_database_path(self) -> Path:
        """Get the actual database file path."""
        if "sqlite" in self.database_url:
            # Extract path from SQLite URL
            url = self.database_url.replace("sqlite+aiosqlite:///", "")
            path = Path(url).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
        return self.data_dir / "brainstream.db"

    def ensure_data_dir(self) -> Path:
        """Ensure data directory exists and return it."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir


# Global settings instance
settings = Settings()
