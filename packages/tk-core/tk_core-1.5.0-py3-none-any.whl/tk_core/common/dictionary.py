from rich import print


def visualize_dict_keys_as_tree(nested_dict: dict, indent: int = 0) -> None:
    """
    Visualizes a nested dictionary as a tree
    """
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            print(" " * indent + f"├── {key}")
            visualize_dict_keys_as_tree(value, indent + 4)
        else:
            print(" " * indent + f"└── {key}")


def deep_find_all(dct: dict, target_key: str) -> list:
    """Recursively find values in nested dictionary by target key."""
    results = []

    for key, value in dct.items():
        if key == target_key:
            results.append(value)
        if isinstance(value, dict):
            results.extend(deep_find_all(value, target_key))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    results.extend(deep_find_all(item, target_key))

    return results


def list_wrap(thing: list | dict) -> list:
    """
    Wrap a dictionary or list in a list.

    Args:
        thing (Union[List[Any], Dict]): The dictionary or list to wrap.

    Returns:
        list: The wrapped dictionary or list.
    """
    if isinstance(thing, list):
        return thing
    else:
        return [thing]


def subset_dict(input: dict, remove_keys: list | None = None) -> dict:
    """Returns a copy of the input dictionary with listed
    keys removed.

    Args:
        input (str): Dictionary to subset
        remove_keys (list[str]): List of keys to omit

    Returns:
        dict: Resulting dictionary
    """
    if remove_keys is None:
        return input.copy()
    output = input.copy()
    [output.pop(k, None) for k in remove_keys]
    return output


def whitelisted_elements(input: dict, accepted_keys: list | None = None) -> dict:
    if accepted_keys is None:
        return {}
    return dict([[k, input.get(k)] for k in accepted_keys])


def combine_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Combines 2 dictionaries into a single dictionary
    All values are converted to lists so that if a key is repeated,
    the values are appended to the list
    """
    combined_dict = {k: v if isinstance(v, list) else [v] for k, v in dict1.items()}

    # Merge values from dict1
    for key, value in dict2.items():
        if key in combined_dict:
            if isinstance(value, list):
                combined_dict[key].extend(value)
            else:
                combined_dict[key].append(value)
        elif isinstance(value, list):
            combined_dict[key] = value
        else:
            combined_dict[key] = [value]

    return {k: list(set(v)) for k, v in combined_dict.items()}


def replace_empty_dict_value(dictionary: dict | list | None) -> dict | list | str | None:
    """
    Recursively replaces empty dictionary values with an empty string
    This is useful for sending variant data to snowflake
    as pyarrow throws an error if the value is an empty dictionary

    Args:
        dictionary (dict|list|None): The variant field to replace empty values in
    """
    if dictionary is None or isinstance(dictionary, (list, str)):
        return dictionary
    elif dictionary == {}:
        return ""
    return {k: replace_empty_dict_value(v) if isinstance(v, dict) else v for k, v in dictionary.items()}
