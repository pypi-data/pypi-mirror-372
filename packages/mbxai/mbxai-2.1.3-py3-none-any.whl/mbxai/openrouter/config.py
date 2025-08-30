from pydantic import BaseModel, Field, field_validator
from typing import Union, Optional
from .models import OpenRouterModel, OpenRouterModelRegistry

class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter client."""
    
    token: str = Field(..., description="OpenRouter API token")
    model: Union[str, OpenRouterModel] = Field(
        default=OpenRouterModel.GPT4_TURBO,
        description="Model to use for completions"
    )
    base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="Base URL for the OpenRouter API"
    )
    default_headers: dict[str, str] = Field(
        default_factory=lambda: {
            "HTTP-Referer": "https://github.com/mibexx/mbxai",
            "X-Title": "MBX AI",
        },
        description="Default headers to include in all requests"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    retry_initial_delay: float = Field(
        default=1.0,
        description="Initial delay between retries in seconds"
    )
    retry_max_delay: float = Field(
        default=10.0,
        description="Maximum delay between retries in seconds"
    )

    @field_validator("token")
    def validate_token(cls, v: str) -> str:
        """Validate that the token is not empty."""
        if not v or not v.strip():
            raise ValueError("Token cannot be empty")
        return v.strip()

    @field_validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        """Validate that the base URL is a valid URL."""
        if not v:
            raise ValueError("Base URL cannot be empty")
        if not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return v.rstrip("/") + "/"  # Always include trailing slash

    @field_validator("model")
    def validate_model(cls, v: Union[str, OpenRouterModel]) -> str:
        """Validate and convert model to string."""
        if isinstance(v, OpenRouterModel):
            return v.value
        if not v:
            raise ValueError("Model cannot be empty")
        
        # Try to get model from registry first
        try:
            return OpenRouterModelRegistry.get_model(v)
        except ValueError:
            # If not in registry, check if it's a valid provider/model format
            if "/" not in v:
                raise ValueError("Custom model must be in format 'provider/model-name'")
            return str(v)

    @field_validator("default_headers")
    def validate_headers(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate that required headers are present and valid."""
        required_headers = {"HTTP-Referer", "X-Title"}
        missing_headers = required_headers - set(v.keys())
        if missing_headers:
            raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")
        
        # Ensure header values are not empty
        empty_headers = [k for k, val in v.items() if not val or not val.strip()]
        if empty_headers:
            raise ValueError(f"Empty values for headers: {', '.join(empty_headers)}")
        
        return {k: val.strip() for k, val in v.items()} 