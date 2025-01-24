# Hierarchical Chain-of-Thought

Breaks down complex problems into hierarchical sections and expands each level systematically.

## Parameters
- `prompt`: The problem statement to analyze
- `depth`: Number of hierarchical levels to create (default: 2)

## Example
```python
from llama_toolbox.reasoning import HierarchicalCoT

depth_chart = [...] # Configure your model stack
hcot = HierarchicalCoT(depth_chart)
result = hcot.fn("Explain quantum computing", depth=3)
```