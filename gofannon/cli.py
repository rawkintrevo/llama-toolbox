import argparse
from .orchestration import ToolChain
from .base import WorkflowContext
from orchestration.firebase_wrapper import FirebaseWrapper
import json

def main():
    parser = argparse.ArgumentParser(description="LLama Toolbox CLI")
    parser.add_argument('--local', action='store_true', help='Run locally')
    parser.add_argument('--firebase', help='Firebase config path')
    parser.add_argument('--workflow', required=True, help='Workflow config JSON')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    # Initialize context
    if args.firebase:
        FirebaseWrapper.initialize(args.firebase)
        context = FirebaseWrapper.get_context('current_workflow')
    else:
        context = WorkflowContext()

        # Load workflow config
    with open(args.workflow) as f:
        workflow_config = json.load(f)

        # Import and instantiate tools
    tools = []
    for tool_config in workflow_config['tools']:
        module = __import__(f".{tool_config['module']}", fromlist=[tool_config['class']])
        tool_class = getattr(module, tool_config['class'])
        tool = tool_class(**tool_config.get('params', {}))
        tools.append(tool)

        # Execute workflow
    chain = ToolChain(tools, context)
    result = chain.execute(workflow_config.get('initial_input', {}))

    # Handle output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result.output, f)
    else:
        print(json.dumps(result.output, indent=2))

        # Save final state
    if args.firebase:
        FirebaseWrapper.save_context('current_workflow', context)
    else:
        context.save_checkpoint('final')

if __name__ == '__main__':
    main()