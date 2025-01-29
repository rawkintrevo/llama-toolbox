from abc import ABC, abstractmethod
import json
from openai import OpenAI
from gofannon.base import BaseTool

sample_depth_chart = [
    {'model_name' : "Qwen/Qwen2.5-72B-Instruct",
     'base_url' : "https://api.deepinfra.com/v1/openai",
     'api_key' : "YOUR_API_KEY_HERE",
     'temperature' : 0.3,
     'prompt_appendix' : '\n\nThinks carefully.'
     }
]

class ReasoningTool(BaseTool, ABC):
    def __init__(self,
                 depth_chart = sample_depth_chart
                 ):
        super().__init__()
        self.depth_chart = depth_chart
        self.error_context = []
        self.jsonify_prompt_s = "Your output should be a properly formatted JSON only. No preamble, explanations, or markdown ticks (```)."


    @abstractmethod
    def fn(self, *args, **kwargs):
        pass

    def create_openai_like_client(self, level: int):
        return OpenAI(
            api_key=self.depth_chart[level]['api_key'],
            base_url=self.depth_chart[level]['base_url']
        )

    def get_response(self, level: int, messages):
        return self.create_openai_like_client(level).chat.completions.create(
            model=self.depth_chart[level]['model_name'],
            messages=messages,
            temperature=self.depth_chart[level]['temperature']
        )

    def get_debug_info(self):
        """Get current debugging information"""
        return {
            "error_context": self.error_context,
            "depth_chart_config": self.depth_chart
        }