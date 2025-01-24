# How to Contribute to LLaMA Toolbox

This guide will walk you through the process of adding a new function to the LLaMA Toolbox repository. We'll cover everything from forking the repo to creating a pull request.

## 1. Fork the Repository
**TODO: Add link to forking in GitHub**

First, you'll need to fork the repository to your own GitHub account. This creates a copy of the repository where you can make changes without affecting the main project.

## 2. What Makes a Good Function?
When proposing a new function, consider these guidelines:

- **Single Responsibility**: Each function should do one thing well
- **Simple Interface**: Keep the API surface small and intuitive
- **Clear Documentation**: Include thorough documentation and examples
- **Error Handling**: Implement proper error handling and logging
- **Modular Design**: If an API has many functions, split them into multiple classes

## 3. Create an Issue
Before starting development, create an issue describing your proposed function:

1. Go to the Issues tab
2. Click "New Issue"
3. Use the "Function Proposal" template
4. Include:
    - Description of the function
    - Use cases
    - Proposed API interface
    - Any dependencies

**TODO: Add link to Issues tab**

## 4. Setting Up Your Development Environment
Clone your forked repository and set up the development environment:

```bash  
git clone https://github.com/YOUR_USERNAME/llama-toolbox.git  
cd llama-toolbox  
pip install -r requirements.txt  
```

## 5. Creating a New Function
### Directory Structure
Add your function under the appropriate directory in `llama-toolbox/`. If it's a new API, create a new directory.

### Base Class Extension
All functions must extend the `BaseTool` class. Here's the basic structure:

```python  
from llama_toolbox.base import BaseTool  
from llama_toolbox.config import FunctionRegistry

@FunctionRegistry.register  
class NewFunction(BaseTool):  
    def __init__(self, name="new_function"):  
        super().__init__()  
        self.name = name

    @property  
    def definition(self):  
        return {  
            "type": "function",  
            "function": {  
                "name": self.name,  
                "description": "Description of what the function does",  
                "parameters": {  
                    "type": "object",  
                    "properties": {  
                        "param1": {  
                            "type": "string",  
                            "description": "Description of param1"  
                        }  
                    },  
                    "required": ["param1"]  
                }  
            }  
        }  
  
    def fn(self, param1):  
        # Implementation goes here  
        try:  
            # Your code  
            return result  
        except Exception as e:  
            self.log_error(f"Error in new_function: {str(e)}")  
            raise  
```

### Required Components
1. **Definition**: The JSON schema defining the function's interface
2. **fn**: The main function implementation
3. **Error Handling**: Proper error handling and logging
4. **Documentation**: Add documentation in the `docs/` directory

### Documentation
Create a markdown file in the appropriate documentation directory:

```markdown
# New Function

## Description
Brief description of what the function does

## Parameters
- `param1`: Description of param1

## Example Usage
```python  
new_func = NewFunction()  
result = new_func.fn("example")  
-```
```

Add a link to your documentation in the appropriate index.md file.

## 6. Testing Your Function

**TODO: Add Tests**

Write unit tests for your function. Create a new test file in the tests/ directory:

```python
import pytest
from llama_toolbox.new_api.new_function import NewFunction

def test_new_function():
func = NewFunction()
result = func.fn("test")
assert result == expected_value
```

## 7. Committing Your Changes

Create a new branch for your feature:

```bash
git checkout -b feature/new-function
```

Add and commit your changes:
```bash
git add .
git commit -m "Add new_function implementation"
```

Push your branch:
```bash
git push origin feature/new-function
```

## 8. Creating a Pull Request

Go to your forked repository on GitHub
Click "Compare & pull request"
Fill out the PR template:
    Description of changes
    Related issues
    Testing performed
Submit the PR

**TODO: Add link to PR creation**

## 9. Code Review

Be prepared to address feedback during code review. Common requests include:

* Adding more test cases
* Improving documentation
* Refactoring for better performance or readability

Tips for Success

* Keep your PRs focused on a single feature
* Write clear commit messages
* Follow the existing code style
* Add comprehensive documentation
* Include meaningful test cases
* Be responsive to code review feedback

** TODO: Create and add link to coding style guide **