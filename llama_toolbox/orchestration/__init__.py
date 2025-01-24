import json
import time
from typing import List, Dict, Any
from ..base import WorkflowContext, ToolResult
from ..config import FunctionRegistry
import logging

logger = logging.getLogger(__name__)

class FunctionOrchestrator:
    def __init__(self, llm_client, tool_configs=None):
        self.logger = logging.getLogger(f"{__name__}.FunctionOrchestrator")
        self.llm = llm_client
        self.available_functions = FunctionRegistry.get_tools()
        self.tool_configs = tool_configs or {}
        self.function_map = self.function_map = self._build_function_map()
        self.logger.debug("Available functions in orchestrator: " + ', '.join(
            [f['function']['name'] for f in self.available_functions]))

    def _build_function_map(self):
        return {
            func_def['function']['name']: (
                FunctionRegistry._tools[func_def['function']['name']],
                self.tool_configs.get(func_def['function']['name'], {})
            ) for func_def in self.available_functions
        }

    def _instantiate_tool(self, function_name):
        tool_class, config = self.function_map[function_name]
        return tool_class(**config)

    def execute_workflow(self, user_query: str, model_name: str, max_steps=5):
        self.logger.debug("Starting workflow execution with query: %s", user_query)
        messages = [{"role": "user", "content": user_query}]
        final_answer = None

        for _ in range(max_steps):
            # Get LLM response
            response = self.llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=self.available_functions
            )
            msg = response.choices[0].message
            messages.append(msg)

            # Check for direct answer first
            if msg.content and not msg.tool_calls:
                final_answer = msg.content
                break

                # Process tool calls if any
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    function_name = tool_call.function.name

                    function_args = json.loads(tool_call.function.arguments)

                    # Execute function
                    # Get tool class and configuration
                    tool_class, config = self.function_map[function_name]

                    # Instantiate tool with configuration
                    tool = tool_class(**config)

                    # Execute function
                    result = tool.fn(**function_args)

                    # Store result in context
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result),#.output,
                        # "name": function_name
                    })
            else:
                break  # Exit if no tools called and no content

        # Final synthesis step
        if not final_answer:
            synthesis_prompt = '''Based on the tool outputs above,   
            provide a complete natural language answer with final numerical result   
            in bold. Follow this format:  
              
            **Final Answer**: [result in bold]   
              
            With supporting calculations shown.'''

            messages.append({"role": "user", "content": synthesis_prompt})

            response = self.llm.chat.completions.create(
                model=model_name,
                messages=messages
            )
            final_answer = response.choices[0].message.content

        return {
            "conversation": messages,
            "final_answer": final_answer
        }

class ToolChain:
    def __init__(self, tools: List[Any], context: WorkflowContext):
        self.tools = tools
        self.context = context

    def _resolve_input(self, input_template: str) -> Any:
        if not input_template:
            return None

        if input_template.startswith('{{') and input_template.endswith('}}'):
            key = input_template[2:-2].strip()
            return self.context.data.get(key)
        return input_template

    def execute(self, initial_input: Dict[str, Any] = None) -> ToolResult:
        self.context.data.update(initial_input or {})

        for tool in self.tools:
            tool_name = tool.__class__.__name__

            # Resolve inputs from context
            resolved_inputs = {
                k: self._resolve_input(v)
                for k, v in tool.definition.get('function', {}).get('parameters', {}).items()
            }

            # Execute tool
            result = tool.execute(self.context, **resolved_inputs)

            if not result.success:
                return result

                # Store output in context
            output_key = f"{tool_name}_output"
            self.context.data[output_key] = result.output

            # Save checkpoint
            self.context.save_checkpoint(f"after_{tool_name}")

        return ToolResult(
            success=True,
            output=self.context.data
        )