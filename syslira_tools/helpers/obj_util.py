from pandas import notna
from typing import Any


def getattr_or_empty_str(obj, attr: str) -> Any:
    """
    Get an attribute from an object or return an empty string if the attribute does not exist.

    Args:
        obj: The object to get the attribute from.
        attr: The name of the attribute.

    Returns:
        str: The value of the attribute or an empty string if it does not exist.
    """
    # Check if the attribute exists in the object or is None

    value = getattr(obj, attr, None)

    if isinstance(value, (list, dict, set)):
        return value

    return value if notna(value) else ""
