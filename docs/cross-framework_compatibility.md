## Cross-Framework Compatibility

The toolbox supports integration with popular AI frameworks:

### LangChain Integration

```python  
# Import LangChain tool  
from langchain.tools import WikipediaQueryRun  
  
# Convert to BaseTool  
lc_tool = WikipediaQueryRun()  
base_tool = BaseTool()  
base_tool.import_from_langchain(lc_tool)  
  
# Use in llama-toolbox workflows  
result = base_tool.fn("machine learning")  
  
# Export back to LangChain  
exported_tool = base_tool.export_to_langchain()  
```

### SmolAgents Integration

```python
# Import SmolAgents tool  
from smolagents.tools import Tool  
  
# Convert to BaseTool  
smol_tool = Tool(...)  
base_tool = BaseTool()  
base_tool.import_from_smolagents(smol_tool)  
  
# Export back to SmolAgents  
exported_tool = base_tool.export_to_smolagents()  
```

Key features:

- Bi-directional conversion preserves metadata and functionality
- Automatic schema translation between frameworks
- Runtime checks for required dependencies

This implementation provides:
- Full type checking and schema validation
- Error handling for missing dependencies
- Bidirectional conversion between frameworks
- Automatic parameter translation
- Comprehensive test coverage
- Documentation examples

The tests verify:
1. Successful tool conversions
2. Parameter schema preservation
3. Functionality equivalence
4. Error handling for missing dependencies
5. Round-trip conversions between frameworks
