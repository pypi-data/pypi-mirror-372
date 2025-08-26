import pytest
from src.extension.apoc import cx


def test_cx_0():
    result = cx(**{'a': 2, 'b': 3})
    assert result == 16

def test_cx_1():
    result = cx(**{'a': 3, 'b': 2})
    assert result == 12
