import pytest
from llama_toolbox.reasoning import HierarchicalCoT, SequentialCoT, TreeOfThought

def test_hierarchical_cot():
    hierarchical_cot = HierarchicalCoT()
    result = hierarchical_cot.fn("Explain quantum computing", depth=3)
    assert result is not None

def test_sequential_cot():
    sequential_cot = SequentialCoT()
    result = sequential_cot.fn("Explain quantum computing", steps=5)
    assert result is not None

def test_tree_of_thought():
    tree_of_thought = TreeOfThought()
    result = tree_of_thought.fn("Explain quantum computing", branches=5)
    assert result is not None