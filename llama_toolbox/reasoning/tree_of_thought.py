 import json
from openai import OpenAI
from .base import ReasoningTool

class TreeOfThought(ReasoningTool):
    def __init__(self, depth_chart):
        super().__init__(depth_chart=depth_chart)
        self.name = "tree_of_thought"

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Tree-of-Thought reasoning with parallel exploration of multiple paths",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The problem prompt to process"
                        },
                        "branches": {
                            "type": "integer",
                            "description": "Number of parallel branches (default: 3)",
                            "default": 3
                        },
                        "evaluation_depth": {
                            "type": "integer",
                            "description": "Depth of evaluation steps (default: 2)",
                            "default": 2
                        }
                    },
                    "required": ["prompt"]
                }
            }
        }

    def fn(self, prompt, branches=3, evaluation_depth=2):
        # Generate initial thought branches
        messages = [{
            "role": "user",
            "content": f"Generate {branches} distinct approaches to solve:\n{prompt}"
        }]

        response = self.get_response(level=0, messages=messages)
        branches = self._parse_branches(response.choices[0].message.content)

        # Evaluate and select best branches
        evaluated = [self._evaluate_branch(b, evaluation_depth) for b in branches]
        sorted_branches = sorted(evaluated, key=lambda x: x['score'], reverse=True)

        return {
            "best_branch": sorted_branches[0],
            "all_branches": sorted_branches
        }

    def _parse_branches(self, content):
        try:
            data = json.loads(content)
            return data.get('branches', [])
        except json.JSONDecodeError:
            return [{"content": content, "score": 0}]

    def _evaluate_branch(self, branch, depth):
        evaluation_prompt = f"""Evaluate this solution approach:  
        {branch}  
          
        Provide a score (0-10) and detailed analysis in JSON format with:  
        - score (integer)  
        - strengths (array)  
        - weaknesses (array)  
        - next_steps (array)"""

        messages = [{"role": "user", "content": evaluation_prompt}]
        response = self.get_response(level=1, messages=messages)

        try:
            evaluation = json.loads(response.choices[0].message.content)
            if depth > 1:
                evaluation['deeper_analysis'] = self._deep_analysis(evaluation)
            return {**branch, **evaluation}
        except json.JSONDecodeError:
            return {**branch, "score": 0, "error": "Evaluation failed"}

    def _deep_analysis(self, evaluation):
        analysis_prompt = f"""Perform deep analysis on:  
        Strengths: {evaluation.get('strengths', [])}  
        Weaknesses: {evaluation.get('weaknesses', [])}  
          
        Provide concrete examples and mitigation strategies in JSON format."""

        response = self.get_response(level=2, messages=[{"role": "user", "content": analysis_prompt}])
        return json.loads(response.choices[0].message.content)