import json
import time
from typing import List, Dict, Any
from ..base import WorkflowContext, ToolResult
from ..config import FunctionRegistry


class FunctionOrchestrator:
    def __init__(self, llm_client, tool_configs=None):
        self.llm = llm_client
        self.available_functions = FunctionRegistry.get_tools()
        self.tool_configs = tool_configs or {}
        self.function_map = self.function_map = self._build_function_map()
        print("Available functions in orchestrator:", ', '.join(
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

    def execute_workflow(self, user_query:str, model_name:str, max_steps=5):
        messages = [{"role": "user", "content": user_query}]

        for _ in range(max_steps):
            # Get LLM response with function calls
            response = self.llm.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=self.available_functions
            )

            # Process function calls
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute function
                tool = self.function_map[function_name]()
                result = tool.fn(**function_args)

                # Store result in context
                messages.append({
                    "role": "tool",
                    "content": str(result),#.output,
                    "name": function_name
                })

        return messages

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