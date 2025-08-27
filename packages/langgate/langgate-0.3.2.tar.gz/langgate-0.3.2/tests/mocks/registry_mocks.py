"""Mock objects for registry testing."""

from langgate.core.models import ImageModelInfo, LLMInfo
from langgate.core.schemas.config import ConfigSchema
from langgate.registry.local import BaseLocalRegistryClient


class CustomLLMInfo(LLMInfo):
    """Custom LLMInfo class for testing subclass handling."""

    custom_field: str = "custom_value"


class CustomImageModelInfo(ImageModelInfo):
    """Custom ImageModelInfo class for testing subclass handling."""

    custom_field: str = "custom_value"


class CustomLocalRegistryClient(
    BaseLocalRegistryClient[CustomLLMInfo, CustomImageModelInfo]
):
    """Custom LocalRegistryClient implementation for testing.

    This is a non-singleton client that uses custom schemas for both LLM and image models.
    """


def create_mock_config() -> ConfigSchema:
    """Create a minimal mock config for testing path resolution."""
    return ConfigSchema.model_validate(
        dict(
            default_params={"text": {"temperature": 0.7}},
            services={
                "openai": {
                    "api_key": "test-key",
                    "base_url": "https://api.openai.com/v1",
                }
            },
            models={
                "text": [
                    {
                        "id": "test/model",
                        "service": {"provider": "openai", "model_id": "test-model"},
                    }
                ]
            },
            app_config={},
        )
    )
