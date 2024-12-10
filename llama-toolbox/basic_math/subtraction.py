from..base import BaseTool

class Subtraction(BaseTool):
    def __init__(self, name="subtraction"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Calculate the difference between two numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "num1": {
                            "type": "number",
                            "description": "The minuend"
                        },
                        "num2": {
                            "type": "number",
                            "description": "The subtrahend"
                        }
                    },
                    "required": ["num1", "num2"]
                }
            }
        }

    def fn(self, num1, num2):
        return num1 - num2