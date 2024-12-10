from abc import ABC, abstractmethod

class BaseTool(ABC):
    def __init__(self):
        self.api_key = None

    @property
    @abstractmethod
    def definition(self):
        """
        Dictionary that should be implemented by subclasses.
        Contains tool metadata and configuration.
        """
        pass

    @abstractmethod
    def fn(self, *args, **kwargs):
        """
        Functionality that should be implemented by subclasses.
        This function should define the core behavior of the tool.
        """
        pass

# Example subclass
class ExampleTool(BaseTool):
    def __init__(self, api_key=None):
        super().__init__()
        self.api_key = api_key

    @property
    def definition(self):
        return {
            "name": "ExampleTool",
            "description": "This is an example tool",
            "version": "1.0.0"
        }

    def fn(self, *args, **kwargs):
        print("Function called with", args, kwargs)
        return "Result"

# Usage
example_tool = ExampleTool(api_key="your_api_key_here")
print(example_tool.definition)
# Output: {'name': 'ExampleTool', 'description': 'This is an example tool', 'version': '1.0.0'}

result = example_tool.fn(1, 2, key='value')
# Output: Function called with (1, 2) {'key': 'value'}
