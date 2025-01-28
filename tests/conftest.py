import pytest
from llama_toolbox.base import BaseTool
from llama_toolbox.config import FunctionRegistry

@pytest.fixture
def tools():
    return [tool_class() for tool_class in FunctionRegistry._tools.values()]