import os
from openai import OpenAI
from .base import BaseAIProvider

class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", os.getenv("OPENAI_API_KEY"))
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"

    def improve_prompt(self, prompt_content, instructions=""):
        user_message = f"Original Prompt:\n{prompt_content}\n\nInstructions: {instructions}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a prompt engineering expert. Clean up and improve the user's prompt so it produces much better AI responses."},
                {"role": "user", "content": user_message}
            ]
        )
        
        improved_text = response.choices[0].message.content
        metadata = {
            "model": self.model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }
        return improved_text, metadata

    def generate_prompt(self, description):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You build clear, professional AI prompts based on what the user wants to accomplish."},
                {"role": "user", "content": f"Task description: {description}"}
            ]
        )
        
        generated_text = response.choices[0].message.content
        metadata = {
            "model": self.model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens
        }
        return generated_text, metadata