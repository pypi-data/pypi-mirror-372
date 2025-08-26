import pathlib

def add(a: int, b: int) -> int:
    """
    加法

    Examples:
        >>> yaml
        input:
          a: 2
          b: 3
        output:
          5
        <<<
        >>> yaml
        input:
          a: 99
          b: 3
        output:
          102
        <<<
    """
    return a + b

def div(a: int, b: int) -> float:
    """
    除法

    Examples:
        >>> yaml
        input:
          a: 6
          b: 3
        output:
          2
        <<<
    """
    if b == 0:
        raise ValueError("divide by zero")
    return a / b