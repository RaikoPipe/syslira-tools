import pandas as pd

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

def detect_unhashable_columns(df):
    """Detect columns containing unhashable types"""
    unhashable_cols = []

    for col in df.columns:
        if df[col].dtype == 'object':
            # Sample non-null values to check
            sample = df[col].dropna().head(100)

            for val in sample:
                try:
                    # Try to hash the value
                    hash(val)
                except TypeError:
                    unhashable_cols.append(col)
                    break

    return unhashable_cols

def clean_unhashable_columns(df, strategy='stringify'):
    """
    Clean unhashable columns in a DataFrame

    Strategies:
    - 'stringify': Convert to string representation
    - 'json': Convert to JSON string
    - 'drop': Remove problematic columns
    - 'expand': Expand dicts to separate columns (dicts only)
    """
    df_clean = df.copy()
    unhashable_cols = detect_unhashable_columns(df)

    if not unhashable_cols:
        return df_clean, []

    print(f"Found unhashable columns: {unhashable_cols}")

    for col in unhashable_cols:
        if strategy == 'stringify':
            df_clean[col] = df_clean[col].astype(str)

        elif strategy == 'json':
            import json
            df_clean[col] = df_clean[col].apply(
                lambda x: json.dumps(x) if x is not None else None
            )

        elif strategy == 'drop':
            df_clean = df_clean.drop(columns=[col])

        elif strategy == 'expand':
            # Only works for dictionaries
            if df_clean[col].apply(lambda x: isinstance(x, dict)).any():
                # Expand dictionaries to separate columns
                expanded = pd.json_normalize(df_clean[col]).add_prefix(f"{col}_")
                df_clean = pd.concat([df_clean.drop(columns=[col]), expanded], axis=1)

    return df_clean, unhashable_cols