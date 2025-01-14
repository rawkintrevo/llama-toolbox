from abc import ABC, abstractmethod
import json
from llama_toolbox.base import BaseTool

class ReasoningTool(BaseTool, ABC):
    def __init__(self, api_key=None,
                 model_name="meta-llama/Llama-3.3-70B-Instruct",
                 temperature=0.3,
                 max_thoughts=5):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_thoughts = max_thoughts

    @abstractmethod
    def fn(self, *args, **kwargs):
        pass
