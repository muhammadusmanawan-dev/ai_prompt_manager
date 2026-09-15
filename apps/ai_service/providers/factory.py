from .openai_providers import OpenAIProvider

class AIProviderFactory:
    _providers = {
        'openai': OpenAIProvider,
    }

    @classmethod
    def get_provider(cls, name="openai"):
        provider_class = cls._providers.get(name.lower())
        if not provider_class:
            raise ValueError(f"Provider '{name}' is not supported.")
        return provider_class()