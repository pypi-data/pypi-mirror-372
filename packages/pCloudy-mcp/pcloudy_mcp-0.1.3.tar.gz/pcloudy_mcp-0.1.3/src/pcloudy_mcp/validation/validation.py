from dotenv import load_dotenv
from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class ValidatedConfig(BaseSettings):
    """Validated environment configuration."""

    pcloudy_username: str = Field(
        ..., min_length=1, description="Username for pCloudy API"
    )
    pcloudy_api_key: str = Field(..., min_length=1, description="API key for pCloudy")
    pcloudy_cloud_url: str = Field(..., min_length=1, description="pCloudy cloud URL")

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",  # Forbid unknown environment variables
    )
