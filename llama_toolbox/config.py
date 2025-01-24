import os
from dotenv import load_dotenv

class ToolConfig:
    _instance = None

    def __init__(self):
        load_dotenv()
        self.config = {
            'github_api_key': os.getenv('GITHUB_API_KEY'),
            'deepinfra_api_key': os.getenv('DEEPINFRA_API_KEY'),
            'arxiv_api_key': os.getenv('ARXIV_API_KEY')
        }

    @classmethod
    def get(cls, key):
        if not cls._instance:
            cls._instance = ToolConfig()
        return cls._instance.config.get(key)

class FunctionRegistry:
    _tools = {}

    @classmethod
    def register(cls, tool_class):
        cls._tools[tool_class().definition['function']['name']] = tool_class
        return tool_class

    @classmethod
    def get_tools(cls):
        return [cls._tools[name]().definition for name in cls._tools]