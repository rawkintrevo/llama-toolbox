import json

def complex_response(prompt: str,
                     tool_desc_list: list[dict],
                     tool_map: dict,
                     openai_like_client,
                     model_name: str = "meta-llama/Llama-3.3-70B-Instruct",
                     system: str = "Think carefully about the problem presented, break it down into a series of steps before attempting to compute.",
                     max_thoughts= 3):
    messages = []
    if system:
        messages.append({
            'role': 'system',
            'content': system
        })
    messages.append({
        'role': 'user',
        'content': prompt
    })
    response = openai_like_client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tool_desc_list,
        tool_choice="auto",
    )
    thoughts = 1
    while (response.choices[0].message.content is None) and (thoughts < max_thoughts):
        thoughts += 1
        print('thinking...')
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)
        process_tool_calls(tool_calls, tool_map, messages)

    messages.append({ 'role' : 'assistant', 'content' : response.choices[0].message.content})
    return {'messages': messages, 'last_response': response}

def process_tool_call(tool_call, tool_map, messages):
    """
    Process a tool call and its potential nested calls.

    Args:
    - tool_call (dict): The tool call to process.
    - tool_map (dict): A dictionary mapping function names to their corresponding functions.
    - messages (list): A list to append the processed messages to.
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
                function_args[key] = process_tool_call(nested_tool_call, tool_map, messages)

                # Check if the function arguments contain any list of values that may contain nested function calls
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict) and 'function' in item and 'arguments' in item['function']:
                        # Recursively process the nested function call
                        nested_tool_call = {
                            'id': tool_call.id,
                            'function': item['function'],
                            'type': 'function'
                        }
                        function_args[key][i] = process_tool_call(nested_tool_call, tool_map, messages)

                        # Process the function call with the updated arguments
        function_response = tool_map[function_name](**function_args)

        # Extend the conversation with the function response
        messages.append({
            "tool_call_id": tool_call.id,
            "role": "tool",
            "content": function_response,
        })

        return function_response

    else:
        # Handle non-function tool calls or errors
        return None

def process_tool_calls(tool_calls, tool_map, messages):
    """
    Process a list of tool calls and their potential nested calls.

    Args:
    - tool_calls (list): A list of tool calls to process.
    - tool_map (dict): A dictionary mapping function names to their corresponding functions.
    - messages (list): A list to append the processed messages to.
    """
    for tool_call in tool_calls:
        process_tool_call(tool_call, tool_map, messages)