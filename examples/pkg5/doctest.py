def run(a, b):
    """
    >>> a = 3
    >>> b = 30
    >>> run(a, b)
    33
    """
    return a + b


def try_doctest():
    """
    >>> try_doctest()
    33
    """
    return run(3, 30)
