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
    port: int = 3001

    # Data directory
    data_dir: Path = Field(
        default=Path.home() / ".brainstream",
        description="Directory for storing application data",
    )

    # ChromaDB
    chroma_persist_dir: Path = Field(
        default=Path.home() / ".brainstream" / "chroma",
        description="ChromaDB persistence directory",
    )

    # SQLite (state management)
    state_db_path: Path = Field(
        default=Path.home() / ".brainstream" / "state.db",
        description="SQLite database for Thompson Sampling state and action logs",
    )

    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # Clustering
    hdbscan_min_cluster_size: int = 5
    hdbscan_min_samples: int = 3

    # LLM
    llm_provider: Literal["claude", "copilot"] = "claude"
    llm_timeout: int = 120

    # Feed
    feed_default_limit: int = 20
    serendipity_slots: int = 2

    def ensure_data_dir(self) -> Path:
        """Ensure data directory exists and return it."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir


# Global settings instance
settings = Settings()
