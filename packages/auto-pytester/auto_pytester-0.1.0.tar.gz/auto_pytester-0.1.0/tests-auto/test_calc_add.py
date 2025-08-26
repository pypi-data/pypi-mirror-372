import pytest
from src.calc import add


def test_add_0():
    result = add(**{'a': 2, 'b': 3})
    assert result == 5

def test_add_1():
    result = add(**{'a': 99, 'b': 3})
    assert result == 102
