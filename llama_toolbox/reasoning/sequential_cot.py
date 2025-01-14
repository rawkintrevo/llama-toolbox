import json
from openai import OpenAI
from llama_toolbox.reasoning.base import ReasoningTool, process_tool_calls

class SequentialCoT(ReasoningTool):
    def __init__(self, api_key=None,
                 model_name="Qwen/Qwen2.5-72B-Instruct",
                 temperature=0.3,
                 base_url="https://api.deepinfra.com/v1/openai",
                 max_thoughts=5):
        super().__init__(api_key, model_name, temperature, max_thoughts)
        self.openai_like_client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.name = "sequential_cot"

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
        modified_prompt = prompt + "\n\nGiven the prompt above, return a series of steps required to arrive at an answer. Do not attempt to compute the answer now, only return the series of steps required to solve the problem. Your response should be a properly formatted json with one field `steps` which contains an array of strings, where each string is a step. Do no include any explanations or ticks to indicate it is a markdown code block."

        messages = [{"role": "user", "content": modified_prompt}]

        response = self.openai_like_client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature
        )

        try:
            steps = json.loads(response.choices[0].message.content)["steps"]
            return steps
        except json.JSONDecodeError:
            return {"error": "Failed to decode the response as JSON."}

    def process_steps(self, steps, tool_map, tool_desc_list, return_type="string"):
        """
        Process each step individually and make subsequent LLM calls.

        Args:
        - steps (list): A list of steps to process.
        - tool_map (dict): A dictionary mapping function names to their corresponding functions.
        - tool_desc_list (list): A list of tool descriptions.
        - return_type (str): The expected return type ("string" or "json").
        """
        messages = []
        results = []

        for step in steps:
            messages.append({"role": "user", "content": step})
            response = self.openai_like_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=tool_desc_list,
                tool_choice="auto",
                temperature=self.temperature
            )

            thoughts = 1
            while (response.choices[0].message.content is None) and (thoughts < self.max_thoughts):
                thoughts += 1
                print('thinking...')
                tool_calls = response.choices[0].message.tool_calls
                messages.append(response.choices[0].message)
                out = process_tool_calls(tool_calls, tool_map, messages, tool_desc_list, self.openai_like_client, return_type)
                messages = out['messages']
                response = out['response']

            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            results.append(response.choices[0].message.content)

        return results