from abc import ABC, abstractmethod
from llama_toolbox.base import BaseTool

class ReasoningTool(BaseTool, ABC):
    def __init__(self, api_key=None,
                 model_name="meta-llama/Llama-3.3-70B-Instruct",
                 temperature=0.3,
                 max_thoughts=5):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_thoughts = max_thoughts

    @abstractmethod
    def fn(self, *args, **kwargs):
        pass

def process_tool_call(tool_call, tool_map, messages, return_type="string"):
    """
    Process a tool call and its potential nested calls.

    Args:
    - tool_call (dict): The tool call to process.
    - tool_map (dict): A dictionary mapping function names to their corresponding functions.
    - messages (list): A list to append the processed messages to.
    - return_type (str): The expected return type ("string" or "json").
    """
    if tool_call.type == 'function':
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Check if the function arguments contain any nested function calls
        for key, value in function_args.items():
            if isinstance(value, dict) and 'function' in value and 'arguments' in value['function']:
                # Recursively process the nested function call
                nested_tool_call = {
                    'id': tool_call['id'],
                    'function': value['function'],
                    'type': 'function'
                }
                function_args[key] = process_tool_call(nested_tool_call, tool_map, messages, return_type)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict) and 'function' in item and 'arguments' in item['function']:
                        # Recursively process the nested function call
                        nested_tool_call = {
                            'id': tool_call.id,
                            'function': item['function'],
                            'type': 'function'
                        }
                        function_args[key][i] = process_tool_call(nested_tool_call, tool_map, messages, return_type)

                        # Process the function call with the updated arguments
        function_response = tool_map[function_name](**function_args)

        # Handle the return type
        if return_type == "json":
            try:
                function_response = json.loads(function_response)
            except json.JSONDecodeError:
                function_response = {"error": "Failed to decode the response as JSON."}

                # Extend the conversation with the function response
        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "content": json.dumps(function_response) if return_type == "json" else function_response,
        })

        return messages

    else:
        # Handle non-function tool calls or errors
        return None

def process_tool_calls(tool_calls, tool_map, messages, tool_desc_list, openai_like_client, return_type="string"):
    """
    Process a list of tool calls and their potential nested calls.

    Args:
    - tool_calls (list): A list of tool calls to process.
    - tool_map (dict): A dictionary mapping function names to their corresponding functions.
    - messages (list): A list to append the processed messages to.
    - tool_desc_list (list): A list of tool descriptions.
    - openai_like_client: The client used to make LLM calls.
    - return_type (str): The expected return type ("string" or "json").
    """
    for tool_call in tool_calls:
        messages = process_tool_call(tool_call, tool_map, messages, return_type)
        response = openai_like_client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=messages,
            tools=tool_desc_list,
            tool_choice="auto",
        )
    return {"messages": messages, "response": response}