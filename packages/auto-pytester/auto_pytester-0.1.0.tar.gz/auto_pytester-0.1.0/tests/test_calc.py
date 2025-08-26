import pytest
from src.calc import add, div
from tests.conftest import project_name


def test_add(project_name):
    print(project_name)
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_div_normal():
    assert div(10, 2) == 5.0

def test_div_by_zero():
    with pytest.raises(ValueError):
        div(10, 0)