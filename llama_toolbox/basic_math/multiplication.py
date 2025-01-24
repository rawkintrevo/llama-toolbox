from..base import BaseTool
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class Multiplication(BaseTool):
    def __init__(self, name="multiplication"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Calculate the product of two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {
                            "type": "number",
                            "description": "The first number"
                        },
                        "num2": {
                            "type": "number",
                            "description": "The second number"
                        }
                    },
                    "required": ["num1", "num2"]
                }
            }
        }

    def fn(self, num1, num2):
        logger.debug(f"Multiplying {num1} by {num2}")
        return num1 * num2