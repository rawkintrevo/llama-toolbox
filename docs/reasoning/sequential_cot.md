# docs/reasoning/sequential_cot.md
# Sequential Chain-of-Thought

The `SequentialCoT` API breaks down complex problems into a sequence of discrete steps, using multiple LLM calls to progressively solve each step.

## Parameters
* `prompt`: The problem statement to solve
* `steps`: Number of steps to generate (configured during initialization)

## Example Usage
```python  
from llama_toolbox.reasoning import SequentialCoT  
  
# Configure model depth chart (typically different models/settings per level)  
depth_chart = [  
    {  
        'model_name': "meta-llama/Llama-3-70B-Instruct",  
        'base_url': "https://api.deepinfra.com/v1/openai",  
        'api_key': "your_api_key",  
        'temperature': 0.3  
    },  
    {  
        'model_name': "meta-llama/Llama-3-13B-Instruct",  
        'base_url': "https://api.example.com/v1",  
        'api_key': "your_api_key",  
        'temperature': 0.5  
    },
    {'model_name' : "meta-llama/Llama-3.3-70B-Instruct",
     'base_url' : "https://api.deepinfra.com/v1/openai",
     'api_key' : "your_api_key",
     'temperature' : 0.3,
     'prompt_appendix' : """Compile all of the previous information into one cohesive document.

     Do not summarize or otherwise truncate the content, except in the case of formatting.

     Your Response should look like a report to an executive."""
     }
]  
  
# Initialize with 5-step process  
scot = SequentialCoT(depth_chart=depth_chart, steps=5)  
result = scot.fn("Explain how photosynthesis works in tropical plants")  
print(result)  
```