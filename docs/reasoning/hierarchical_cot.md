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

## Background

The Hierarchical Chain-of-Thought (HierarchicalCoT) approach is inspired by two key sources: (1) the paper "In-Context Decision Transformer: Reinforcement Learning via Hierarchical Chain-of-Thought" by Sili Huang et al., and (2) practical applications of hierarchical reasoning in creative and educational contexts, such as generating multi-level content structures (e.g., TV series, degree programs).

### Key Findings from the Paper:

The paper introduces the **In-Context Decision Transformer (IDT)**, which leverages hierarchical decision-making to improve the efficiency and performance of reinforcement learning tasks. Key insights include:

1. **Hierarchical Decision-Making**: The paper demonstrates that high-level decisions can guide multi-step low-level actions, significantly reducing the computational complexity of long-horizon tasks. This approach mirrors human decision-making, where abstract high-level decisions (e.g., budgeting for a trip) guide more granular actions (e.g., choosing transportation modes).

2. **Efficiency Gains**: By structuring decisions hierarchically, IDT achieves a 36× reduction in evaluation time on the D4RL benchmark and a 27× reduction on the Grid World benchmark compared to traditional methods. This efficiency stems from shorter across-episodic contexts, which reduce the quadratic complexity of self-attention mechanisms.

3. **Self-Improvement**: IDT enables self-improvement through trial-and-error at test time without requiring gradient updates. This is achieved by constructing across-episodic contexts that serve as memory and search mechanisms for better decision-making.

4. **Application in RL**: The paper validates IDT on both short-horizon (Grid World) and long-horizon (D4RL) tasks, showing state-of-the-art performance. The hierarchical structure allows IDT to handle sparse rewards and complex tasks more effectively than traditional methods.

### Application in HierarchicalCoT:

The HierarchicalCoT function in the LLaMA Toolbox is designed to mimic the hierarchical reasoning process described in the paper and applied in creative workflows. Key applications include:

1. **Multi-Level Problem Solving**: HierarchicalCoT breaks down complex problems into a hierarchy of sub-problems, similar to how IDT decomposes RL tasks into high-level decisions and low-level actions. This approach is particularly useful for tasks requiring structured reasoning, such as generating multi-level content (e.g., TV series, degree programs).

2. **Efficient Exploration**: By generating high-level outlines first (e.g., a series outline, season arcs, episode structures), HierarchicalCoT reduces the complexity of generating detailed content. This mirrors the efficiency gains observed in IDT, where high-level decisions guide low-level actions.

3. **Iterative Refinement**: HierarchicalCoT supports iterative refinement at each level of the hierarchy. For example, after generating a high-level outline, users can refine individual sections (e.g., episodes, modules) before generating detailed content. This aligns with the trial-and-error process in IDT, where high-level decisions are refined based on feedback from low-level actions.

4. **Creative and Educational Use Cases**: HierarchicalCoT has been applied to creative tasks like generating TV series scripts and educational tasks like designing degree programs. In these applications, the function first generates a high-level structure (e.g., series outline, degree program), then progressively refines each level (e.g., season arcs, course modules) before producing detailed content (e.g., scripts, lecture notes).

By combining insights from the IDT paper and practical applications, HierarchicalCoT provides a powerful tool for structured reasoning and content generation in both creative and technical domains.  

For more details, refer to the original paper: 
[In-Context Decision Transformer: Reinforcement Learning via Hierarchical Chain-of-Thought](https://arxiv.org/abs/2405.20692).
