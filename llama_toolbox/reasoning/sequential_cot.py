import json
from openai import OpenAI
from llama_toolbox.reasoning.base import ReasoningTool

class SequentialCoT(ReasoningTool):
    def __init__(self, api_key=None,
                 model_name="Qwen/Qwen2.5-72B-Instruct",
                 temperature=0.3,
                 base_url="https://api.deepinfra.com/v1/openai",
                 steps = 3,
                 max_thoughts=5):
        super().__init__(api_key, model_name, temperature, max_thoughts)
        self.openai_like_client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.name = "sequential_cot"
        self.steps = 3

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

        response = self.openai_like_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature
        )

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
                response = self.openai_like_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature
                )
                step_output.append(response.choices[0].message.content)
                messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
            return "\n".join(step_output)
        except json.JSONDecodeError:
            return {"error": "Failed to decode the response as JSON."}

