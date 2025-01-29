import json
import logging
from openai import OpenAI, APIError
from.base import ReasoningTool
from ..config import FunctionRegistry

logger = logging.getLogger(__name__)

@FunctionRegistry.register
class HierarchicalCoT(ReasoningTool):
    def __init__(self, depth_chart= None):
        super().__init__(depth_chart=depth_chart)
        self.name = "hierarchical_cot"
        self.depth_chart = depth_chart or []
        self.error_context = []  # Track error locations

    @property
    def definition(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Hierarchical Chain-of-Thought reasoning with outline generation and section expansion",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The problem prompt to process"
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Depth of hierarchy (default: 2)",
                            "default": 2
                        }
                    },
                    "required": ["prompt"]
                }
            }
        }

    def fn(self, prompt, depth=2):
        self.error_context = []  # Reset error tracking
        if depth > len(self.depth_chart):
            return {"error": f"Requested depth {depth} exceeds configured model levels {len(self.depth_chart)}"}

        try:
            if depth < 1:
                raise ValueError("Depth must be at least 1")

            outline = self._generate_outline(prompt, depth)
            if 'error' in outline:
                return outline

            return self._expand_sections(outline, current_depth=1, max_depth=depth)

        except Exception as e:
            logger.error(f"Critical failure: {str(e)}")
            return {
                "error": "HierarchicalCoT processing failed",
                "context": self.error_context,
                "exception": str(e)
            }

    def _generate_outline(self, prompt, depth):
        try:
            outline_prompt = f"""Organize this problem into a {depth}-level hierarchical structure:    
            {prompt}    
              
            Your output should be a properly formatted JSON only. No preamble, explanations, or markdown ticks (```).   
            Return JSON format with keys 'title' and 'sections' (array of section objects).   
            """
            if depth > 1:
                outline_prompt += "Each section should have 'title' and 'sections'. "

            messages = [{"role": "user", "content": outline_prompt}]
            response = self.get_response(level=0, messages=messages)

            try:
                structure = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError as e:
                self.error_context.append({
                    "stage": "outline_parsing",
                    "response": response.choices[0].message.content,
                    "error": str(e)
                })
                return {"error": "Invalid JSON structure in outline"}

                # Validate outline structure
            if not isinstance(structure, dict):
                self.error_context.append({
                    "stage": "outline_validation",
                    "structure_type": type(structure).__name__,
                    "expected_type": "dict"
                })
                return {"error": "Outline structure is not a dictionary"}

            required_keys = {'title', 'sections'}
            if not required_keys.issubset(structure.keys()):
                self.error_context.append({
                    "stage": "outline_validation",
                    "missing_keys": list(required_keys - structure.keys())
                })
                return {"error": f"Outline missing required keys: {required_keys}"}

            return structure

        except APIError as e:
            self.error_context.append({
                "stage": "outline_generation",
                "error_type": "APIError",
                "status_code": e.status_code,
                "message": e.message
            })
            return {"error": "API failure during outline generation"}

        except Exception as e:
            self.error_context.append({
                "stage": "outline_generation",
                "error_type": type(e).__name__,
                "message": str(e)
            })
            return {"error": "Unexpected error during outline generation"}

    def _expand_sections(self, node, current_depth, max_depth, path=None):
        if path is None:
            path = []

        current_path = path + [node.get('title', 'Untitled Section')]

        if current_depth >= max_depth:
            return node

        if current_depth >= len(self.depth_chart):
            self.error_context.append({
                "stage": "depth_validation",
                "current_depth": current_depth,
                "max_configured_depth": len(self.depth_chart)-1
            })
            raise ValueError("Current depth exceeds configured model depth chart")

        try:
            client = self.create_openai_like_client(current_depth)
            expanded = node.copy()

            if 'sections' in node:
                for i, section in enumerate(node['sections']):
                    logger.debug(f"Expanding section {i+1}/{len(node['sections'])} at depth {current_depth}")

                    next_depth = current_depth + 1
                    is_final_depth = next_depth == max_depth

                    # Generate appropriate prompt based on depth
                    if is_final_depth:
                        expansion_prompt = f"""Expand this section within the context of: {" -> ".join(current_path)}    
                          
                        Section to expand: {section['title']}      
                        Current depth: {current_depth}/{max_depth}      
                          
                        Provide detailed content for this section. The content should be a concise explanation.  
                        Your output should be a properly formatted JSON only with a 'content' field.   
                        No preamble, explanations, or markdown ticks (```). """
                    else:
                        expansion_prompt = f"""Expand this section within the context of: {" -> ".join(current_path)}    
                          
                        Section to expand: {section['title']}      
                        Current depth: {current_depth}/{max_depth}      
                          
                        Provide detailed sub-sections in JSON format with 'title' and 'sections'.    
                        Your output should be a properly formatted JSON only. No preamble, explanations, or markdown ticks (```). """

                    try:
                        response = client.chat.completions.create(
                            model=self.depth_chart[current_depth]['model_name'],
                            messages=[{"role": "user", "content": expansion_prompt}],
                            temperature=self.depth_chart[current_depth]['temperature']
                        )
                    except APIError as e:
                        self.error_context.append({
                            "stage": f"section_expansion_depth_{current_depth}",
                            "section_index": i,
                            "section_title": section.get('title'),
                            "error_type": "APIError",
                            "status_code": e.status_code,
                            "message": e.message
                        })
                        continue

                    if not response.choices:
                        self.error_context.append({
                            "stage": f"section_expansion_depth_{current_depth}",
                            "section_index": i,
                            "error": "Empty API response"
                        })
                        continue

                    try:
                        expanded_section = json.loads(response.choices[0].message.content)
                    except json.JSONDecodeError as e:
                        self.error_context.append({
                            "stage": f"section_parsing_depth_{current_depth}",
                            "section_index": i,
                            "response": response.choices[0].message.content,
                            "error": str(e)
                        })
                        continue

                        # Handle content generation for final depth
                    if is_final_depth:
                        if 'content' not in expanded_section:
                            self.error_context.append({
                                "stage": f"content_validation_depth_{current_depth}",
                                "section_index": i,
                                "response": expanded_section
                            })
                            continue

                            # Update section with content and remove subsections
                        expanded['sections'][i]['content'] = expanded_section['content']
                        if 'sections' in expanded['sections'][i]:
                            del expanded['sections'][i]['sections']
                    else:
                        # Validate section structure and recursively expand
                        if not isinstance(expanded_section, dict) or 'title' not in expanded_section:
                            self.error_context.append({
                                "stage": f"section_validation_depth_{current_depth}",
                                "section_index": i,
                                "response_structure": type(expanded_section).__name__
                            })
                            continue

                        expanded['sections'][i] = self._expand_sections(
                            expanded_section,
                            next_depth,
                            max_depth,
                            current_path
                        )

            return expanded

        except Exception as e:
            self.error_context.append({
                "stage": f"section_expansion_depth_{current_depth}",
                "error_type": type(e).__name__,
                "message": str(e),
                "node": node.get('title')[:100] if 'title' in node else str(node)[:100]
            })
            raise

    def get_debug_info(self):
        return {
            "error_context": self.error_context,
            "depth_chart_config": self.depth_chart
        }

    def to_markdown(self, output):
        def _to_markdown(node, level=1):
            markdown = ""

            if 'title' in node:
                title = node['title']
                markdown += f"{'#' * level} {title}\n\n"

            if 'content' in node:
                markdown += f"{node['content']}\n\n"

            if 'sections' in node:
                for section in node['sections']:
                    markdown += _to_markdown(section, level + 1)

            return markdown
        return _to_markdown(output)