from..base import BaseTool
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class Division(BaseTool):
    def __init__(self, name="division"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Calculate the quotient of two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {
                            "type": "number",
                            "description": "The dividend"
                        },
                        "num2": {
                            "type": "number",
                            "description": "The divisor"
                        }
                    },
                    "required": ["num1", "num2"]
                }
            }
        }

    def fn(self, num1, num2):
        logger.debug(f"Dividing {num1} by {num2}")
        if num2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return num1 / num2  