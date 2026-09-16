import os
from anthropic import Anthropic
from .base import BaseAIProvider


class AnthropicProvider(BaseAIProvider):
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
        self.max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "1024"))

    def _complete(self, system_prompt, user_prompt):
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        metadata = {
            "model": self.model,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
        }
        return response.content[0].text, metadata 

    def improve_prompt(self, prompt_content, instructions=""):
        return self._complete(
            "You are a prompt engineering expert. Clean up and improve the user's prompt so it produces much better AI responses.",
            f"Original Prompt:\n{prompt_content}\n\nInstructions: {instructions}",
        )

    def generate_prompt(self, description):
        return self._complete(
            "You build clear, professional AI prompts based on what the user wants to accomplish.",
            f"Task description: {description}",
        )
