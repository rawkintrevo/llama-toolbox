import json
import logging
from openai import OpenAI, APIError
from .base import ReasoningTool
from ..config import FunctionRegistry

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class TreeOfThought(ReasoningTool):
    def __init__(self, depth_chart= None):
        super().__init__(depth_chart=depth_chart)
        self.name = "tree_of_thought"
        self.depth_chart = depth_chart or []

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
        logger.debug(f"Tree of Thought. {branches} branches. {evaluation_depth} depth.")
        self.error_context = []  # Reset error tracking
        try:
            if 0 >= len(self.depth_chart):
                self.error_context.append({
                    "stage": "initialization",
                    "error": "No models configured in depth_chart"
                })
                return {"error": "No models configured in depth_chart"}

                # Generate initial thought branches
            messages = [{
                "role": "user",
                "content": f"Generate {branches} distinct approaches to solve:"
                           f"{prompt}"
                           f"Your output MUST be a JSON object containing a 'branches' key with an array of {branches} approach strings."  
                           """Example format: {{"branches": ["Approach 1", "Approach 2"]}}"""
                           f"{self.jsonify_prompt_s}"
            }]

            response = self._safe_get_response(0, messages, "initial_branch_generation")
            if "error" in response:
                return response

            parsed_branches = self._parse_branches(response)
            if "error" in parsed_branches:
                return parsed_branches

                # Evaluate and select best branches
            evaluated = []
            for i, branch in enumerate(parsed_branches.get('branches', [])):
                evaluated_branch = self._evaluate_branch(branch, evaluation_depth, branch_index=i)
                evaluated.append(evaluated_branch)

            sorted_branches = sorted(evaluated, key=lambda x: x.get('score', 0), reverse=True)

            return {
                "best_branch": sorted_branches[0] if sorted_branches else None,
                "all_branches": sorted_branches,
                "debug_info": self.get_debug_info()  # Include debug info in response
            }

        except Exception as e:
            logger.error(f"Critical failure: {str(e)}", exc_info=True)
            self.error_context.append({
                "stage": "fn_execution",
                "error_type": type(e).__name__,
                "message": str(e)
            })
            return {
                "error": "TreeOfThought processing failed",
                "context": self.error_context,
                "exception": str(e),
                "debug_info": self.get_debug_info()  # Include debug info in error response
            }

    # Update the _parse_branches method to handle different structures:
    def _parse_branches(self, response):
        try:
            content = response.choices[0].message.content
            try:
                data = json.loads(content)

                # Handle case where response is a direct array
                if isinstance(data, list):
                    processed = [{'description': b} if isinstance(b, str) else b for b in data]
                    return {"branches": processed}

                    # Handle case where branches are under different keys
                for key in ['branches', 'approaches', 'solutions']:
                    if key in data and isinstance(data[key], list):
                        branches = data[key]
                        processed = []
                        for b in branches:
                            if isinstance(b, str):
                                processed.append({'description': b})
                            else:
                                processed.append(b)
                        return {"branches": processed}

                        # Validate branches structure
                if not isinstance(data.get('branches', []), list):
                    raise ValueError("Branches should be a list")

                    # Process branches to ensure they are dictionaries
                branches = data.get('branches', [])
                processed = []
                for b in branches:
                    if isinstance(b, str):
                        processed.append({'description': b})
                    else:
                        processed.append(b)
                data['branches'] = processed

                return data

            except json.JSONDecodeError as e:
                self.error_context.append({
                    "stage": "branch_parsing",
                    "response": content,
                    "error": str(e)
                })
                return {"error": "Invalid JSON structure in branches"}

        except AttributeError as e:
            self.error_context.append({
                "stage": "branch_generation",
                "error_type": "AttributeError",
                "message": str(e)
            })
            return {"error": "Invalid API response structure"}

    def _evaluate_branch(self, branch, depth, branch_index):
        try:
            evaluation_prompt = f"""Evaluate this solution approach:    
            {branch}    
              
            Provide a score (0-10) and detailed analysis in JSON format with:    
            - score (integer)    
            - strengths (array)    
            - weaknesses (array)    
            - next_steps (array)\n\n{self.jsonify_prompt_s}"""

            response = self._safe_get_response(1, [{"role": "user", "content": evaluation_prompt}],
                                               f"branch_evaluation_{branch_index}")
            if "error" in response:
                return {**branch, "score": 0, "error": response["error"]}

            try:
                evaluation = json.loads(response.choices[0].message.content)
                if not isinstance(evaluation.get('score', 0), int):
                    raise ValueError("Score must be integer")
            except (json.JSONDecodeError, ValueError) as e:
                self.error_context.append({
                    "stage": f"evaluation_parsing_{branch_index}",
                    "response": response.choices[0].message.content,
                    "error": str(e)
                })
                evaluation = {"score": 0, "error": str(e)}

            if depth > 1:
                evaluation['deeper_analysis'] = self._deep_analysis(evaluation, branch_index)

            return {**branch, **evaluation}

        except Exception as e:
            self.error_context.append({
                "stage": f"branch_evaluation_{branch_index}",
                "error_type": type(e).__name__,
                "message": str(e)
            })
            return {**branch, "score": 0, "error": "Evaluation failed"}

    def _deep_analysis(self, evaluation, branch_index):
        try:
            analysis_prompt = f"""Perform deep analysis on:    
            Strengths: {evaluation.get('strengths', [])}    
            Weaknesses: {evaluation.get('weaknesses', [])}    
              
            Provide concrete examples and mitigation strategies in JSON format.\n\n{self.jsonify_prompt_s}"""

            response = self._safe_get_response(2, [{"role": "user", "content": analysis_prompt}],
                                               f"deep_analysis_{branch_index}")
            if "error" in response:
                return {"error": response["error"]}

            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError as e:
                self.error_context.append({
                    "stage": f"deep_analysis_parsing_{branch_index}",
                    "response": response.choices[0].message.content,
                    "error": str(e)
                })
                return {"error": "Deep analysis parsing failed"}

        except Exception as e:
            self.error_context.append({
                "stage": f"deep_analysis_{branch_index}",
                "error_type": type(e).__name__,
                "message": str(e)
            })
            return {"error": "Deep analysis failed"}

    def _safe_get_response(self, level, messages, context_stage):
        try:
            if level >= len(self.depth_chart):
                error_msg = f"Level {level} not configured in depth_chart"
                self.error_context.append({
                    "stage": context_stage,
                    "error": error_msg
                })
                return {"error": error_msg}

            return self.get_response(level=level, messages=messages)
        except APIError as e:
            self.error_context.append({
                "stage": context_stage,
                "error_type": "APIError",
                "status_code": e.status_code,
                "message": e.message
            })
            return {"error": f"API Error: {e.message}"}
        except Exception as e:
            self.error_context.append({
                "stage": context_stage,
                "error_type": type(e).__name__,
                "message": str(e)
            })
            return {"error": str(e)}