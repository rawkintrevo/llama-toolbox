import json
from openai import OpenAI
from llama_toolbox.reasoning.base import ReasoningTool

class SequentialCoT(ReasoningTool):
    def __init__(self, depth_chart, steps):
        super().__init__(depth_chart= depth_chart)
        self.name = "sequential_cot"
        self.steps = steps

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Generate a series of steps required to solve a problem using Chain-of-Thought reasoning.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to generate steps for."
                        }
                    },
                    "required": ["prompt"]
                }
            }
        }

    def fn(self, prompt):
        modified_prompt = prompt + f"""
        
Given the prompt above, return a series of {self.steps} steps required to arrive at an answer. 
Do not attempt to compute the answer now, only return the series of steps 
required to solve the problem, as a series of prompts to future LLM calls. Your 
response should be a properly formatted json with one field `steps` which contains
 an array of strings, where each string is a step. Do no include any explanations
  or ticks to indicate it is a markdown code block."""

        messages = [{"role": "user", "content": modified_prompt}]

        response = self.get_response(level= 0 , messages= messages)
        messages= [
            {'role': 'user', 'content': prompt},
            {'role' : 'assistant', 'content':response.choices[0].message.content}
        ]

        try:
            steps = json.loads(response.choices[0].message.content)["steps"]
            step_output = []
            for i in range(len(steps)):
                print(f"thinking about Step {i+1}/{len(steps)}:'{steps[i]}'...")
                messages.append({'role': 'user', 'content': steps[i]})

                response = self.get_response(level= 1, messages= messages)
                step_output.append(response.choices[0].message.content)
                messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
            messages.append({'role': 'user', 'content': self.depth_chart[2]})
            response = self.get_response(level = 2, messages= messages)
            return response
        except json.JSONDecodeError:
            return {"error": "Failed to decode the response as JSON."}

