"""
Utility functions for the sample project.
Testing various function signatures and documentation.
"""

def simple_function():
    """Function with no parameters."""
    return "Hello, World!"


def function_with_params(name: str, age: int, active: bool = True):
    """
    Function with multiple parameters and default values.
    
    Args:
        name: The person's name
        age: The person's age
        active: Whether the person is active
    """
    return f"{name} is {age} years old"


def function_with_return(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y


def complex_function(
    items: list,
    callback = None,
    *args,
    **kwargs
) -> dict:
    """
    Complex function with various parameter types.
    
    Args:
        items: List of items to process
        callback: Optional callback function
        *args: Variable positional arguments
        **kwargs: Variable keyword arguments
        
    Returns:
        Dictionary with results
    """
    result = {"count": len(items)}
    if callback:
        result["processed"] = [callback(item) for item in items]
    return result
