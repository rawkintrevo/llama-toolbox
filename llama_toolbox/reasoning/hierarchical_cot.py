# llama_toolbox/reasoning/hierarchical_cot.py  

def _expand_sections(self, node, current_depth, max_depth, path=None):
    if path is None:
        path = []

        # Create current section path
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

                # Include hierarchical context in prompt
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

                    # Validate section structure
                if not isinstance(expanded_section, dict) or 'title' not in expanded_section:
                    self.error_context.append({
                        "stage": f"section_validation_depth_{current_depth}",
                        "section_index": i,
                        "response_structure": type(expanded_section).__name__
                    })
                    continue

                    # Recursively expand with updated path
                expanded['sections'][i] = self._expand_sections(
                    expanded_section,
                    current_depth + 1,
                    max_depth,
                    current_path  # Pass updated hierarchical path
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