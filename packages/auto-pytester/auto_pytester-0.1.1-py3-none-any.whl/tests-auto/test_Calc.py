import pytest


from src.calc import Calc

@pytest.fixture
def calc():
    return Calc()



def test_Calc_add_1(calc):
    
    
    result = calc.add(**{'a': 2, 'b': 3})
    assert result == 5

def test_Calc_add_2(calc):
    
    
    result = calc.add(**{'a': 99, 'b': 3})
    assert result == 102

def test_Calc_div_1(calc):
    
    
    result = calc.div(**{'a': 6, 'b': 3})
    assert result == 2
