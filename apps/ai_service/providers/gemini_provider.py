import os

from google import genai

from .base import BaseAIProvider


class GeminiProvider(BaseAIProvider):

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.6-flash"

    def improve_prompt(self, prompt_content, instructions=""):
        user_message = (
            f"Original Prompt:\n{prompt_content}\n\n"
            f"Instructions: {instructions}"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                "You are a prompt engineering expert. "
                "Clean up and improve the user's prompt so it "
                "produces much better AI responses.\n\n"
                f"{user_message}"
            ),
        )

        improved_text = response.text

        metadata = {
            "model": self.model,
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "completion_tokens": response.usage_metadata.candidates_token_count,
        }

        return improved_text, metadata

    def generate_prompt(self, description):
        response = self.client.models.generate_content(
            model=self.model,
            contents=(
                "You build clear, professional AI prompts based on "
                "what the user wants to accomplish.\n\n"
                f"Task description: {description}"
            ),
        )

        generated_text = response.text

        metadata = {
            "model": self.model,
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "completion_tokens": response.usage_metadata.candidates_token_count,
        }

        return generated_text, metadata