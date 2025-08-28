
def cx(a: int, b: int) -> float:
    """
    位运算 - 左移

    Examples:
        >>> yaml
        doc: 2 << 3 == 16 ?
        input:
          a: 2
          b: 3
        output:
          16
        <<<
        >>> yaml
        input:
          a: 3
          b: 2
        output:
          12
        <<<
    """
    return a << b