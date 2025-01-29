import pytest
from gofannon.basic_math import Addition, Subtraction, Multiplication, Division, Exponents

def test_addition():
    addition = Addition()
    result = addition.fn(2, 3)
    assert result == 5

def test_subtraction():
    subtraction = Subtraction()
    result = subtraction.fn(5, 3)
    assert result == 2

def test_multiplication():
    multiplication = Multiplication()
    result = multiplication.fn(4, 5)
    assert result == 20

def test_division():
    division = Division()
    result = division.fn(10, 2)
    assert result == 5.0

def test_exponents():
    exponents = Exponents()
    result = exponents.fn(2, 3)
    assert result == 8