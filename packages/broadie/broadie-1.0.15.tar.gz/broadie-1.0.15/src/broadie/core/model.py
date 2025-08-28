"""
Simplified model management for Broadie agents.
"""

from typing import Any, Dict, Optional, Union

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from broadie.config.settings import BroadieSettings
from broadie.utils.exceptions import ModelError


def get_default_model(
    settings: Optional[BroadieSettings] = None,
) -> ChatGoogleGenerativeAI:
    """
    Get the default configured model.

    Args:
        settings: Optional settings override

    Returns:
        Configured ChatGoogleGenerativeAI model
    """
    if settings is None:
        settings = BroadieSettings()

    return ChatGoogleGenerativeAI(
        model=settings.default_model,
        temperature=0.2,
        max_tokens=50000,
        timeout=None,
        max_retries=2,
    )


def create_model(
    model_name: str = "gemini-2.0-flash", provider: str = "google", **kwargs
) -> Any:
    """
    Create a language model with specified configuration.

    Args:
        model_name: Name of the model
        provider: Model provider (currently only google supported)
        **kwargs: Additional model parameters

    Returns:
        Configured ChatGoogleGenerativeAI model

    Raises:
        ModelError: If model creation fails
    """
    try:
        model_config = {
            "model": model_name,
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 50000),
            "max_retries": kwargs.get("max_retries", 2),
            "timeout": kwargs.get("timeout"),
        }

        # Remove None values
        model_config = {k: v for k, v in model_config.items() if v is not None}

        if provider == "google":
            return ChatGoogleGenerativeAI(**model_config)
        else:
            # Use init_chat_model for other providers (fallback)
            return init_chat_model(
                model=model_name, model_provider=provider, **model_config
            )

    except Exception as e:
        raise ModelError(
            f"Failed to create model {model_name} with provider {provider}: {str(e)}"
        ) from e


def create_model_from_config(
    config: Dict[str, Any], settings: Optional[BroadieSettings] = None
) -> Any:
    """
    Create a language model from configuration dictionary.

    Args:
        config: Model configuration
        settings: Broadie settings

    Returns:
        Configured language model
    """
    model_name = config.get("name", "gemini-2.0-flash")
    provider = config.get("provider", "google")

    # Extract model-specific settings
    model_kwargs = {k: v for k, v in config.items() if k not in ["name", "provider"]}

    return create_model(
        model_name=model_name, provider=provider, settings=settings, **model_kwargs
    )


class ModelManager:
    """
    Simplified model manager for Broadie agents.
    """

    def __init__(self, settings: Optional[BroadieSettings] = None):
        self.settings = settings or BroadieSettings()
        self._default_model = None

    def get_default_model(self) -> ChatGoogleGenerativeAI:
        """Get the default model instance, cached."""
        if self._default_model is None:
            self._default_model = get_default_model(self.settings)
        return self._default_model

    def create_model(self, model_name: str = None, **kwargs) -> Any:
        """Create a new model instance."""
        model_name = model_name or self.settings.default_model
        return create_model(model_name=model_name, **kwargs)


# Global model manager
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get the global model manager."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager
