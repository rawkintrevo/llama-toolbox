
import pytest
from gofannon.base import BaseTool
from gofannon.basic_math import Addition

# LangChain tests
def test_langchain_import_export():
    try:
        from langchain.tools import BaseTool as LangchainBaseTool
        from langchain.tools import WikipediaQueryRun
    except ImportError:
        pytest.skip("langchain-core not installed")

        # Test import from LangChain
    lc_tool = WikipediaQueryRun()
    base_tool = BaseTool()
    base_tool.import_from_langchain(lc_tool)

    assert base_tool.name == "wikipedia"
    assert "Wikipedia" in base_tool.description
    assert "query" in base_tool.definition['function']['parameters']

    # Test export to LangChain
    exported_tool = base_tool.export_to_langchain()
    assert isinstance(exported_tool, LangchainBaseTool)
    result = exported_tool.run("machine learning")
    assert "Machine learning" in result

def test_smolagents_import_export():
    try:
        from smolagents.tools import Tool as SmolTool
    except ImportError:
        pytest.skip("smolagents not installed")

        # Create test smolagent tool
    def test_fn(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    smol_tool = SmolTool(
        name="test_addition",
        description="Adds numbers",
        inputs={
            "a": {"type": "int", "description": "First number"},
            "b": {"type": "int", "description": "Second number"}
        },
        output_type="int",
        forward=test_fn
    )

    # Test import from smolagents
    base_tool = BaseTool()
    base_tool.import_from_smolagents(smol_tool)

    assert base_tool.name == "test_addition"
    assert "Adds numbers" in base_tool.description
    assert "a" in base_tool.definition['function']['parameters']

    # Test export to smolagents
    exported_tool = base_tool.export_to_smolagents()
    assert exported_tool.forward(2, 3) == 5

def test_cross_framework_roundtrip():
    # Create native tool
    native_tool = Addition()

    # Export to LangChain
    lc_tool = native_tool.export_to_langchain()

    # Import back as BaseTool
    imported_tool = BaseTool()
    imported_tool.import_from_langchain(lc_tool)

    assert imported_tool.fn(2, 3) == 5
    assert imported_tool.name == "addition"

    # Test with smolagents
    exported_smol = native_tool.export_to_smolagents()
    assert exported_smol.forward(4, 5) == 9