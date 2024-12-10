from..base import BaseTool

class Addition(BaseTool):
    def __init__(self, name="addition"):
        super().__init__()
        self.name = name

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Calculate the sum of two numbers",
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
        return num1 + num2