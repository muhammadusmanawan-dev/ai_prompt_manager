from abc import ABC, abstractmethod

class BaseAIProvider(ABC):

    @abstractmethod
    def improve_prompt(self, prompt_content, instructions=""):
        pass

    @abstractmethod
    def generate_prompt(self, description):
        pass