# docs/reasoning/sequential_cot.md
# Sequential Chain-of-Thought

The `SequentialCoT` API breaks down complex problems into a sequence of discrete steps, using multiple LLM calls to progressively solve each step.

## Parameters
* `prompt`: The problem statement to solve
* `steps`: Number of steps to generate (configured during initialization)

## Depth Chart

- **Level 1:** This is the model that generates the steps/action plan. 
- **Level 2:** This is the model that will execute each step. 
- **Level 3:** This is the model that will synthesize the final result.

## Example Usage

```python  
from gofannon.reasoning import SequentialCoT

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
    {'model_name': "meta-llama/Llama-3.3-70B-Instruct",
     'base_url': "https://api.deepinfra.com/v1/openai",
     'api_key': "your_api_key",
     'temperature': 0.3,
     'prompt_appendix': """Compile all of the previous information into one cohesive document.

     Do not summarize or otherwise truncate the content, except in the case of formatting.

     Your Response should look like a report to an executive."""
     }
]

# Initialize with 5-step process  
scot = SequentialCoT(depth_chart=depth_chart, steps=5)
result = scot.fn("Explain how photosynthesis works in tropical plants")
print(result)  
```

## Background

The Sequential Chain-of-Thought (SequentialCoT) API is inspired by the findings presented in the paper *"Large Language Models are Zero-Shot Reasoners"* by Takeshi Kojima et al. (2022). The paper demonstrates that large language models (LLMs) can perform complex multi-step reasoning tasks effectively by simply prompting them with a step-by-step reasoning instruction, such as "Let's think step by step." This approach, referred to as Zero-shot Chain-of-Thought (Zero-shot-CoT), significantly improves the performance of LLMs on tasks requiring logical, arithmetic, and symbolic reasoning without the need for task-specific few-shot examples.

The key insight from the paper is that LLMs inherently possess the capability to break down complex problems into a sequence of discrete steps when prompted appropriately. This capability is particularly useful for tasks that require multi-step reasoning, such as arithmetic word problems, commonsense reasoning, and symbolic manipulation. The SequentialCoT API leverages this insight by providing a structured way to elicit step-by-step reasoning from LLMs, enabling them to solve problems more effectively.

### Key Findings from the Paper:
1. **Zero-shot Reasoning**: The paper shows that LLMs can perform zero-shot reasoning by simply adding a prompt like "Let's think step by step" before generating an answer. This approach outperforms standard zero-shot prompting and achieves significant improvements across various reasoning tasks.

2. **Versatility**: The Zero-shot-CoT method is versatile and can be applied across diverse reasoning tasks, including arithmetic (e.g., MultiArith, GSM8K), symbolic reasoning (e.g., Last Letter Concatenation), and commonsense reasoning (e.g., StrategyQA), without requiring task-specific prompts or examples.

3. **Scaling Laws**: The effectiveness of Zero-shot-CoT improves with the size of the language model. Larger models, such as GPT-3 and PaLM, show more pronounced improvements in reasoning performance when prompted with step-by-step instructions.

4. **Error Analysis**: The paper highlights that while Zero-shot-CoT often produces logically correct reasoning paths, it can sometimes fail due to commonsense mistakes or unnecessary steps. However, the generated reasoning paths are generally understandable and can be used to debug errors.

### Application in SequentialCoT:
The SequentialCoT API builds on these findings by providing a framework for breaking down complex problems into a sequence of steps, each handled by a different model or configuration. This approach allows for more controlled and interpretable reasoning, as each step can be fine-tuned or adjusted independently. The API supports multiple levels of reasoning, with each level potentially using a different model or temperature setting, enabling users to tailor the reasoning process to their specific needs.

For more details, refer to the original paper:    
[Kojima, T., Gu, S. S., Reid, M., Matsuo, Y., & Iwasawa, Y. (2022). *Large Language Models are Zero-Shot Reasoners*. arXiv preprint arXiv:2205.11916.](https://arxiv.org/abs/2205.11916)  