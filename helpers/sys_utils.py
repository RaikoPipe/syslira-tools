import inspect
from smolagents.tools import Tool

def get_tool_functions_from_modules(*modules):
    """Get all functions decorated with @tool from a specific module."""
    tool_functions = []

    for module in modules:
        for name, obj in inspect.getmembers(module):
            if hasattr(obj, "description"):
                tool_functions.append(obj)

    return tool_functions

