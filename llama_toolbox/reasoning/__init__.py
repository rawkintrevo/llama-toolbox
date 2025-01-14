from .sequential_cot import SequentialCoT
from .base import process_tool_calls
import json

def complex_response(prompt: str,
                     tool_desc_list: list[dict],
                     tool_map: dict,
                     openai_like_client,
                     model_name: str = "meta-llama/Llama-3.3-70B-Instruct",
                     system: str = "Think carefully about the problem presented, break it down into a series of steps before attempting to compute.",
                     max_thoughts: int= 3,
                     temperature: float=0.3):
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

    # Use SequentialCoT to generate steps
    sequential_cot = SequentialCoT(api_key=openai_like_client.api_key, model_name=model_name, temperature=temperature, max_thoughts=max_thoughts)
    steps = sequential_cot.fn(prompt)

    # Append steps to messages
    messages.append({
        'role': 'assistant',
        'content': json.dumps({"steps": steps})
    })

    response = openai_like_client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tool_desc_list,
        tool_choice="auto",
        temperature=temperature
    )

    thoughts = 1
    while (response.choices[0].message.content is None) and (thoughts < max_thoughts):
        thoughts += 1
        print('thinking...')
        tool_calls = response.choices[0].message.tool_calls
        messages.append(response.choices[0].message)
        out = process_tool_calls(tool_calls,
                                 tool_map,
                                 messages,
                                 tool_desc_list,
                                 openai_like_client)
        messages = out['messages']
        response = out['response']

    messages.append({ 'role' : 'assistant', 'content' : response.choices[0].message.content})
    return {'messages': messages, 'last_response': response}  