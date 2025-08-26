import pytest
from src.calc import div


def test_div_0():
    result = div(**{'a': 6, 'b': 3})
    assert result == 2
