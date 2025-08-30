"""OpenRouter models and model registry."""

from enum import Enum
from typing import ClassVar

class OpenRouterModel(str, Enum):
    """Built-in OpenRouter models."""

    GPT4_TURBO = "openai/gpt-4-turbo-preview"
    GPT4 = "openai/gpt-4"
    GPT41 = "openai/gpt-4.1"
    GPT35_TURBO = "openai/gpt-3.5-turbo"
    CLAUDE_3_OPUS = "anthropic/claude-3-opus"
    CLAUDE_3_SONNET = "anthropic/claude-3-sonnet"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku"
    GEMINI_PRO = "google/gemini-pro"
    MIXTRAL_8X7B = "mistral/mixtral-8x7b"
    MISTRAL_MEDIUM = "mistral/mistral-medium"
    MISTRAL_SMALL = "mistral/mistral-small"
    MISTRAL_TINY = "mistral/mistral-tiny"

class OpenRouterModelRegistry:
    """Registry for OpenRouter models."""

    _custom_models: ClassVar[dict[str, str]] = {}
    _initialized: ClassVar[bool] = False

    @classmethod
    def _initialize(cls) -> None:
        """Initialize the registry if not already initialized."""
        if not cls._initialized:
            cls._custom_models = {}
            cls._initialized = True

    @classmethod
    def register_model(cls, name: str, value: str) -> None:
        """Register a new model.

        Args:
            name: The name of the model (e.g., "CUSTOM_MODEL")
            value: The model identifier (e.g., "provider/model-name")

        Raises:
            ValueError: If the model name is already registered.
        """
        cls._initialize()
        if name in cls._custom_models:
            # If the value is the same, just return
            if cls._custom_models[name] == value:
                return
            raise ValueError(f"Model {name} is already registered")
        cls._custom_models[name] = value

    @classmethod
    def get_model(cls, name: str) -> str:
        """Get a model by name.

        Args:
            name: The name of the model

        Returns:
            The model identifier

        Raises:
            ValueError: If the model is not found.
        """
        cls._initialize()
        try:
            return OpenRouterModel[name].value
        except KeyError:
            try:
                return cls._custom_models[name]
            except KeyError:
                raise ValueError(f"Model {name} not found")

    @classmethod
    def list_models(cls) -> dict[str, str]:
        """List all available models.

        Returns:
            A dictionary mapping model names to their identifiers.
        """
        cls._initialize()
        return {
            **{model.name: model.value for model in OpenRouterModel},
            **cls._custom_models,
        } 