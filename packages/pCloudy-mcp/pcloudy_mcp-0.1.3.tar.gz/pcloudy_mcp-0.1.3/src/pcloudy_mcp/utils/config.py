"""Configuration management with proper validation."""

from typing import Any, Dict

from ..validation.validation import ValidatedConfig

# Create the validated config instance once
_validated = ValidatedConfig()


class UserDetail:
    def __init__(self, validated_config: ValidatedConfig) -> None:
        self.pcloudy_username = validated_config.pcloudy_username
        self.pcloudy_api_key = validated_config.pcloudy_api_key
        self.pcloudy_cloud_url = str(validated_config.pcloudy_cloud_url)


class Config:
    def __init__(self) -> None:
        self.userdetail = UserDetail(_validated)

    def __bool__(self) -> bool:
        """Return True if configuration is valid."""
        return bool(
            self.userdetail.pcloudy_username
            and self.userdetail.pcloudy_api_key
            and self.userdetail.pcloudy_cloud_url
        )

    def get_device_settings(self) -> Dict[str, Any]:
        """Get device management settings for tools."""
        return {
            "pcloudy_username": self.userdetail.pcloudy_username,
            "pcloudy_password": self.userdetail.pcloudy_api_key,  # Using API key as password
            "pcloudy_base_url": self.userdetail.pcloudy_cloud_url,
        }
