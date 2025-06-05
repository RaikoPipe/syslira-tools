
def convert_inverted_index(inverted_index: dict) -> str:
    """
    Map inverted index to a string.

    Args:
        inverted_index: The inverted index

    Returns:
        str: The string representation of the inverted index
    """
    # Create a dictionary mapping indices to items with dictionary comprehension
    index_to_item = {index: item for item, indices in inverted_index.items() for index in indices}

    spaces_added_text = {index: f" {item}" for index, item in index_to_item.items() if
                         item not in [",", ".", "(", ")", "[", "]", "{", "}", ":", ";", "!", "?"] and index != 0}
    spaces_added_text = index_to_item | spaces_added_text

    # Sort by indices and join the items
    return ''.join(spaces_added_text[index] for index in sorted(spaces_added_text))


