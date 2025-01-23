from..base import BaseTool
from ..config import FunctionRegistry

@FunctionRegistry.register
class Exponents(BaseTool):
    def __init__(self, name="exponents"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Calculate the result of a number raised to a power",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base": {
                            "type": "number",
                            "description": "The base number"
                        },
                        "power": {
                            "type": "number",
                            "description": "The power to which the base is raised"
                        }
                    },
                    "required": ["base", "power"]
                }
            }
        }

    def fn(self, base, power):
        return base ** power