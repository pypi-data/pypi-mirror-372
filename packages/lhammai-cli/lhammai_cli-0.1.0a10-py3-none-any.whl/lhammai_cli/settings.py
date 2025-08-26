import os
from pathlib import Path

from any_llm.exceptions import UnsupportedProviderError
from any_llm.provider import ProviderFactory
from dotenv import find_dotenv, load_dotenv
from pydantic import AnyHttpUrl, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings

load_dotenv(find_dotenv(".default.env", usecwd=True))
load_dotenv(find_dotenv(".env", usecwd=True), override=True)

DEFAULT_MODEL = os.getenv("MODEL", "ollama:gemma3:4b")
DEFAULT_API_BASE = os.getenv("API_BASE", "http://localhost:11434")


class Settings(BaseSettings):
    """Set application settings."""

    # LLM settings
    model: str = Field(validation_alias="MODEL", default=DEFAULT_MODEL)
    api_base: str = Field(validation_alias="API_BASE", default=DEFAULT_API_BASE)

    # logging
    log_level: str = Field(validation_alias="LOG_LEVEL", default="DEBUG")
    log_file: str = Field(validation_alias="LOG_FILE", default="app.log")
    log_retention: str = Field(validation_alias="LOG_RETENTION", default="10 days")

    # conversation history
    history_file: Path = Field(validation_alias="HISTORY_FILE", default=Path("~/.lhammai/history.json").expanduser())

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate that the model follows the expected format.

        Check that the model string is in the format '<provider>:<model>'
        and that the provider is in the `SUPPORTED_PROVIDERS` list.
        """
        try:
            _, _ = ProviderFactory.split_model_provider(v)
        except UnsupportedProviderError:
            raise
        except ValidationError:
            raise

        return v

    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> AnyHttpUrl:
        """Convert API base URL string to AnyHttpUrl."""
        return AnyHttpUrl(v)


settings = Settings()  # type: ignore
