# Tree-of-Thought

Explores multiple reasoning paths in parallel and selects the most promising one.


## Parameters

- `prompt`: Problem statement to solve 
- `branches`: Number of parallel paths to explore (default: 3)
- `evaluation_depth`: Depth of evaluation steps (default: 2)

## Example

```python
from llama_toolbox.reasoning import TreeOfThought

depth_chart = [...] # Configure your model stack  
tot = TreeOfThought(depth_chart)  
result = tot.fn("Develop a climate change mitigation plan", branches=5)  
```