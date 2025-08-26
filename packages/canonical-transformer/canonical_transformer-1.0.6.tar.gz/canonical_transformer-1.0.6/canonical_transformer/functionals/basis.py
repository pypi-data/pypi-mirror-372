from functools import reduce

def pipe(*functions):
    """
    Compose function for left-to-right composition
    """
    return lambda *args, **kwargs: reduce(
        lambda acc, f: f(acc), 
        functions[1:], 
        functions[0](*args, **kwargs)
    )

def compose(*functions):
    """
    Compose function for right-to-left composition
    """
    return lambda *args, **kwargs: reduce(
        lambda acc, f: f(acc), 
        reversed(functions[:-1]), 
        functions[-1](*args, **kwargs)
    )