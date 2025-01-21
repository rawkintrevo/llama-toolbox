import json
from openai import OpenAI
from .base import ReasoningTool

class HierarchicalCoT(ReasoningTool):
    def __init__(self, depth_chart):
        super().__init__(depth_chart=depth_chart)
        self.name = "hierarchical_cot"

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
        # Generate initial outline
        outline_prompt = f"""Organize this problem into a {depth}-level hierarchical structure:  
        {prompt}  
          
        Return JSON format with keys 'title' and 'sections' (array of section objects).
        Onlv return a valid JSON (no preable, summary or ```).
        """

        if depth > 1:
            outline_prompt = outline_prompt + "Each section should have 'title' and 'subsections' (if depth > 1)."
        messages = [{"role": "user", "content": outline_prompt}]
        response = self.get_response(level=0, messages=messages)
        print(response)
        try:
            structure = json.loads(response.choices[0].message.content)
            return self._expand_sections(structure, current_depth=1, max_depth=depth)
        except json.JSONDecodeError:
            return {"error": "Failed to generate valid structure"}

    def _expand_sections(self, node, current_depth, max_depth):
        if current_depth >= max_depth:
            return node

        client = self.create_openai_like_client(current_depth)
        expanded = node.copy()

        if 'sections' in node:
            for i, section in enumerate(node['sections']):
                expansion_prompt = f"""Expand this section: {section['title']}  
                Current depth: {current_depth}/{max_depth}  
                Provide detailed sub-sections in JSON format with 'title' and 'sections'."""

                response = client.chat.completions.create(
                    model=self.depth_chart[current_depth]['model_name'],
                    messages=[{"role": "user", "content": expansion_prompt}],
                    temperature=self.depth_chart[current_depth]['temperature']
                )

                expanded_section = json.loads(response.choices[0].message.content)
                expanded['sections'][i] = self._expand_sections(
                    expanded_section,
                    current_depth+1,
                    max_depth
                )

        return expanded