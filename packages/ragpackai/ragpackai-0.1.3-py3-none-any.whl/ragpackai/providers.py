"""
Provider mapping and lazy loading for ragpackai.

This module handles the mapping of provider names to their corresponding
embedding and LLM classes, with lazy imports to avoid forcing heavy
installations unnecessarily.
"""

import importlib
from typing import Dict, Any, Optional, Type, Union
import warnings


class ProviderError(Exception):
    """Raised when a provider is not available or misconfigured."""
    pass


class LazyImport:
    """Lazy import wrapper that imports modules only when accessed."""
    
    def __init__(self, module_name: str, class_name: str, install_hint: str = None):
        self.module_name = module_name
        self.class_name = class_name
        self.install_hint = install_hint or f"pip install {module_name.split('.')[0]}"
        self._cached_class = None
    
    def get_class(self) -> Type:
        """Get the class, importing if necessary."""
        if self._cached_class is None:
            try:
                module = importlib.import_module(self.module_name)
                self._cached_class = getattr(module, self.class_name)
            except ImportError as e:
                raise ProviderError(
                    f"Failed to import {self.class_name} from {self.module_name}. "
                    f"Install the required dependencies with: {self.install_hint}"
                ) from e
            except AttributeError as e:
                raise ProviderError(
                    f"Class {self.class_name} not found in {self.module_name}"
                ) from e
        return self._cached_class


# Embedding provider mappings
EMBEDDING_PROVIDERS = {
    "openai": {
        "class": LazyImport(
            "langchain_openai",
            "OpenAIEmbeddings",
            "pip install langchain-openai"
        ),
        "models": {
            "text-embedding-3-small": {"dimensions": 1536},
            "text-embedding-3-large": {"dimensions": 3072},
            "text-embedding-ada-002": {"dimensions": 1536},
        }
    },
    "huggingface": {
        "class": LazyImport(
            "langchain_community.embeddings",
            "HuggingFaceEmbeddings",
            "pip install sentence-transformers"
        ),
        "models": {
            "all-MiniLM-L6-v2": {"dimensions": 384},
            "all-mpnet-base-v2": {"dimensions": 768},
            "multi-qa-MiniLM-L6-cos-v1": {"dimensions": 384},
        }
    },
    "hf": "huggingface",  # Alias
    "google": {
        "class": LazyImport(
            "langchain_google_genai",
            "GoogleGenerativeAIEmbeddings",
            "pip install langchain-google-genai"
        ),
        "models": {
            "models/embedding-001": {"dimensions": 768},
            "models/text-embedding-004": {"dimensions": 768},
        }
    },
    "google-vertex": {
        "class": LazyImport(
            "langchain_google_vertexai",
            "VertexAIEmbeddings",
            "pip install langchain-google-vertexai"
        ),
        "models": {
            "textembedding-gecko": {"dimensions": 768},
            "textembedding-gecko-multilingual": {"dimensions": 768},
            "text-embedding-004": {"dimensions": 768},
        }
    }
}

# LLM provider mappings
LLM_PROVIDERS = {
    "openai": {
        "class": LazyImport(
            "langchain_openai",
            "ChatOpenAI",
            "pip install langchain-openai"
        ),
        "models": [
            # GPT-5 series
            "gpt-5", "gpt-5-pro", "gpt-5-mini", "gpt-5-nano", "gpt-5-thinking",
            # GPT-4.1 series
            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano",
            # GPT-4o (multimodal tier-limited, but still usable as chat model)
            "gpt-4o", "gpt-4o-mini",
            # Legacy / transitional
            "o4-mini", "gpt-4.5",
            # GPT-4 Turbo & GPT-3.5
            "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
            # OpenAI OSS models
            "gpt-oss-120b", "gpt-oss-20b"
        ]
    },
    "google": {
        "class": LazyImport(
            "langchain_google_genai",
            "ChatGoogleGenerativeAI",
            "pip install langchain-google-genai"
        ),
        "models": [
            # Stable Gemini 2.5
            "gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite",
            "gemini-live-2.5-flash",
            # Preview Gemini 2.5
            "gemini-2.5-flash-image-preview", "gemini-live-2.5-flash-preview",
            # Older supported
            "gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash",
            "gemini-1.5-flash-8b", "gemini-2.0-flash-exp"
        ]
    },
    "google-vertex": {
        "class": LazyImport(
            "langchain_google_vertexai",
            "ChatVertexAI",
            "pip install langchain-google-vertexai"
        ),
        "models": [
            "gemini-pro", "gemini-pro-vision",
            "gemini-1.5-pro", "gemini-1.5-flash",
            "chat-bison", "codechat-bison"
        ]
    },
    "groq": {
        "class": LazyImport(
            "langchain_groq",
            "ChatGroq",
            "pip install ragpackai[groq]"
        ),
        "models": [
            # Groq-native
            "mixtral-8x7b-32768", "llama2-70b-4096",
            # OpenAI OSS via Groq
            "openai/gpt-oss-120b", "openai/gpt-oss-20b",
            # Accessible through Groq Chat interface
            "gemma-7b", "mistral-8x7b",
            "llama-3-8b", "llama-3-70b"
        ]
    },
    "cerebras": {
        "class": LazyImport(
            "langchain_cerebras",
            "ChatCerebras",
            "pip install ragpackai[cerebras]"
        ),
        "models": [
            # Standard
            "llama3.1-8b", "llama3.1-70b",
            # Newer Llama 4 preview
            "llama-4-scout-17b-16e-instruct",
            "llama-4-maverick-17b-128e-instruct",
            # Qwen previews
            "qwen-3-32b", "qwen-3-235b-a22b-instruct-2507",
            "qwen-3-235b-a22b-thinking-2507", "qwen-3-coder-480b",
            # Other llama variants
            "llama-3.3-70b"
        ]
    }
}



def _validate_model_availability(provider: str, model_name: str, provider_type: str) -> None:
    """
    Validate if a model is available for a provider.

    Args:
        provider: Provider name
        model_name: Model name
        provider_type: 'embedding' or 'llm'
    """
    providers_map = EMBEDDING_PROVIDERS if provider_type == 'embedding' else LLM_PROVIDERS

    if provider in providers_map:
        provider_config = providers_map[provider]
        if isinstance(provider_config, dict) and "models" in provider_config:
            available_models = provider_config["models"]

            # For embedding providers, check if model exists in the models dict
            if provider_type == 'embedding' and isinstance(available_models, dict):
                if model_name not in available_models:
                    warnings.warn(
                        f"Model '{model_name}' not found in known models for {provider}. "
                        f"Available models: {list(available_models.keys())}. "
                        f"The model might still work if it's a valid model name.",
                        UserWarning
                    )

            # For LLM providers, check if model exists in the models list
            elif provider_type == 'llm' and isinstance(available_models, list):
                if model_name not in available_models:
                    warnings.warn(
                        f"Model '{model_name}' not found in known models for {provider}. "
                        f"Available models: {available_models}. "
                        f"The model might still work if it's a valid model name.",
                        UserWarning
                    )


def get_embedding_provider(provider: str, model_name: str, **kwargs) -> Any:
    """
    Get an embedding provider instance.

    Args:
        provider: Provider name (e.g., 'openai', 'huggingface', 'google')
        model_name: Model name (e.g., 'text-embedding-3-small')
        **kwargs: Additional arguments to pass to the provider

    Returns:
        Embedding provider instance

    Raises:
        ProviderError: If provider is not supported or dependencies missing
    """
    # Handle aliases
    if provider in EMBEDDING_PROVIDERS and isinstance(EMBEDDING_PROVIDERS[provider], str):
        provider = EMBEDDING_PROVIDERS[provider]

    if provider not in EMBEDDING_PROVIDERS:
        available = [k for k in EMBEDDING_PROVIDERS.keys() if not isinstance(EMBEDDING_PROVIDERS[k], str)]
        raise ProviderError(f"Unsupported embedding provider: {provider}. Available: {available}")

    # Validate model availability
    _validate_model_availability(provider, model_name, 'embedding')

    provider_config = EMBEDDING_PROVIDERS[provider]
    provider_class = provider_config["class"].get_class()

    # Prepare arguments based on provider
    if provider == "openai":
        return provider_class(model=model_name, **kwargs)
    elif provider in ["huggingface", "hf"]:
        return provider_class(model_name=model_name, **kwargs)
    elif provider == "google":
        # Use API key authentication for Google Generative AI
        api_key = kwargs.pop('google_api_key', None) or kwargs.pop('api_key', None)
        if not api_key:
            import os
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ProviderError(
                "Google API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable "
                "or pass google_api_key parameter."
            )

        return provider_class(model=model_name, google_api_key=api_key, **kwargs)
    elif provider == "google-vertex":
        return provider_class(model_name=model_name, **kwargs)
    else:
        return provider_class(model=model_name, **kwargs)


def get_llm_provider(provider: str, model_name: str, **kwargs) -> Any:
    """
    Get an LLM provider instance.

    Args:
        provider: Provider name (e.g., 'openai', 'google', 'groq')
        model_name: Model name (e.g., 'gpt-4o-mini')
        **kwargs: Additional arguments to pass to the provider

    Returns:
        LLM provider instance

    Raises:
        ProviderError: If provider is not supported or dependencies missing
    """
    if provider not in LLM_PROVIDERS:
        available = list(LLM_PROVIDERS.keys())
        raise ProviderError(f"Unsupported LLM provider: {provider}. Available: {available}")

    # Validate model availability
    _validate_model_availability(provider, model_name, 'llm')

    provider_config = LLM_PROVIDERS[provider]
    provider_class = provider_config["class"].get_class()

    # Set default temperature if not provided
    if "temperature" not in kwargs:
        kwargs["temperature"] = 0.0

    # Handle Google provider authentication
    if provider == "google":
        # Use API key authentication for Google Generative AI
        api_key = kwargs.pop('google_api_key', None) or kwargs.pop('api_key', None)
        if not api_key:
            import os
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

        if not api_key:
            raise ProviderError(
                "Google API key not found. Please set GOOGLE_API_KEY or GEMINI_API_KEY environment variable "
                "or pass google_api_key parameter."
            )

        return provider_class(model=model_name, google_api_key=api_key, **kwargs)
    elif provider == "google-vertex":
        return provider_class(model=model_name, **kwargs)
    else:
        return provider_class(model=model_name, **kwargs)


def get_embedding_dimensions(provider: str, model_name: str) -> Optional[int]:
    """
    Get the embedding dimensions for a given provider and model.
    
    Args:
        provider: Provider name
        model_name: Model name
        
    Returns:
        Number of dimensions or None if unknown
    """
    # Handle aliases
    if provider in EMBEDDING_PROVIDERS and isinstance(EMBEDDING_PROVIDERS[provider], str):
        provider = EMBEDDING_PROVIDERS[provider]
    
    if provider not in EMBEDDING_PROVIDERS:
        return None
    
    provider_config = EMBEDDING_PROVIDERS[provider]
    if "models" in provider_config and model_name in provider_config["models"]:
        return provider_config["models"][model_name].get("dimensions")
    
    return None


def parse_model_string(model_string: str) -> tuple[str, str]:
    """
    Parse a model string in format 'provider:model' or just 'model'.
    
    Args:
        model_string: Model string to parse
        
    Returns:
        Tuple of (provider, model_name)
        
    Examples:
        >>> parse_model_string("openai:gpt-4o-mini")
        ("openai", "gpt-4o-mini")
        >>> parse_model_string("gpt-4o-mini")
        ("openai", "gpt-4o-mini")  # Default to openai
    """
    if ":" in model_string:
        provider, model_name = model_string.split(":", 1)
        return provider.strip(), model_name.strip()
    else:
        # Default to openai for backward compatibility
        return "openai", model_string.strip()


def validate_provider_config(config: Dict[str, Any], config_type: str) -> None:
    """
    Validate a provider configuration.
    
    Args:
        config: Configuration dictionary with 'provider' and 'model_name' keys
        config_type: Type of config ('embedding' or 'llm')
        
    Raises:
        ProviderError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ProviderError(f"Invalid {config_type} config: must be a dictionary")
    
    if "provider" not in config:
        raise ProviderError(f"Missing 'provider' in {config_type} config")
    
    if "model_name" not in config:
        raise ProviderError(f"Missing 'model_name' in {config_type} config")
    
    provider = config["provider"]
    
    if config_type == "embedding":
        if provider not in EMBEDDING_PROVIDERS:
            available = [k for k in EMBEDDING_PROVIDERS.keys() if not isinstance(EMBEDDING_PROVIDERS[k], str)]
            raise ProviderError(f"Unsupported embedding provider: {provider}. Available: {available}")
    elif config_type == "llm":
        if provider not in LLM_PROVIDERS:
            available = list(LLM_PROVIDERS.keys())
            raise ProviderError(f"Unsupported LLM provider: {provider}. Available: {available}")
