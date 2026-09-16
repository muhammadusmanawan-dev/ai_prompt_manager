from .anthropic_provider import AnthropicProvider
from .openai_providers import OpenAIProvider
from .gemini_provider import GeminiProvider


class AIProviderFactory:
    _providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'gemini': GeminiProvider,
    }

    @classmethod
    def get_provider(cls, name="openai"):
        provider_class = cls._providers.get(name.lower())

        if not provider_class:
            raise ValueError(f"Provider '{name}' is not supported.")

        return provider_class()