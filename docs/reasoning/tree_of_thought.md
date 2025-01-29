# Tree-of-Thought

Explores multiple reasoning paths in parallel and selects the most promising one.


## Parameters

- `prompt`: Problem statement to solve 
- `branches`: Number of parallel paths to explore (default: 3)
- `evaluation_depth`: Depth of evaluation steps (default: 2)

## Depth Chart

- **Level N:** This is the model that generates the branch at level N. This model keeps exploring
trees until they reach `evaluation_depth`

## Example

```python
from gofannon.reasoning import TreeOfThought

depth_chart = [...]  # Configure your model stack  
tot = TreeOfThought(depth_chart)
result = tot.fn("Develop a climate change mitigation plan", branches=5)  
```

## Background

The Tree-of-Thought (ToT) framework is inspired by the paper [*"Tree of Thoughts: Deliberate Problem Solving with Large Language Models"* by Shunyu Yao et al. (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601). This paper introduces a novel approach to enhance the problem-solving capabilities of large language models (LLMs) by enabling them to explore multiple reasoning paths in parallel, evaluate intermediate steps, and backtrack when necessary. The ToT framework generalizes the popular Chain-of-Thought (CoT) approach, allowing LMs to perform deliberate decision-making by considering diverse reasoning paths and self-evaluating choices.

### Key Findings from the Paper:

1. **Limitations of Existing Methods**: Traditional LLMs, such as GPT-4, are confined to token-level, left-to-right decision-making during inference. This limits their ability to handle tasks requiring exploration, strategic lookahead, or backtracking, especially in complex problem-solving scenarios.

2. **Tree-of-Thought Framework**: The ToT framework introduces a tree-like structure where each node represents a coherent unit of text (a "thought") that serves as an intermediate step toward solving a problem. This allows LMs to explore multiple reasoning paths, evaluate their progress, and make global decisions by looking ahead or backtracking.

3. **Deliberate Decision-Making**: ToT enables LMs to self-evaluate intermediate thoughts, compare different reasoning paths, and select the most promising one. This is achieved through search algorithms like breadth-first search (BFS) and depth-first search (DFS), which guide the exploration of the solution space.

4. **Empirical Results**: The paper demonstrates that ToT significantly improves problem-solving abilities on tasks requiring non-trivial planning or search, such as the Game of 24, Creative Writing, and Mini Crosswords. For example, in the Game of 24, ToT achieved a success rate of 74%, compared to only 4% with standard CoT prompting.

5. **Modularity and Adaptability**: The ToT framework is modular, allowing for variations in thought decomposition, generation, evaluation, and search algorithms. This adaptability makes it suitable for a wide range of tasks, from mathematical reasoning to creative problem-solving.

### Application in TreeOfThought:

The `TreeOfThought` function in the LLaMA Toolbox implements the ToT framework by enabling parallel exploration of multiple reasoning paths and evaluating their potential outcomes. Key features include:

- **Parallel Exploration**: The `TreeOfThought` function explores multiple reasoning paths simultaneously, allowing the LM to consider diverse approaches to solving a problem. This is particularly useful for tasks requiring non-linear or exploratory reasoning.

- **Self-Evaluation**: The function incorporates a self-evaluation mechanism where the LM assesses the viability of different reasoning paths. This is achieved through prompts that encourage the LM to evaluate the strengths, weaknesses, and potential outcomes of each thought.

- **Backtracking**: If a reasoning path leads to a dead-end or is deemed less promising, the function can backtrack to previous steps and explore alternative directions. This mirrors the human problem-solving process of trial and error.

- **Search Algorithms**: The function supports search algorithms like BFS and DFS, which guide the exploration of the solution space. These algorithms are adapted to the nature of the problem, ensuring efficient and systematic exploration.

- **Flexibility**: The `TreeOfThought` function is designed to be flexible, allowing users to customize the depth of exploration, the number of parallel paths, and the evaluation criteria. This makes it adaptable to a wide range of tasks, from mathematical reasoning to creative writing.

By incorporating the principles outlined in the paper, the `TreeOfThought` function enhances the problem-solving capabilities of LLaMA-based models, enabling them to tackle complex tasks that require deliberate reasoning and strategic planning.  

For more details, refer to the original paper:
["Tree of Thoughts: Deliberate Problem Solving with Large Language Models"* by Shunyu Yao et al. (arXiv:2305.10601).](https://arxiv.org/abs/2305.10601)