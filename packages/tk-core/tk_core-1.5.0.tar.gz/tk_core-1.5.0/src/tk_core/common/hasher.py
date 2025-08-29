"""Common hashing functions for data engineering"""

import hashlib

HASH_VERSION = "v1"


def uri_and_hash_from_dict(params: dict, remove_keys: list = None) -> tuple:
    """Convenience function to convert a dictionary to
    both a uri string and versioned hash. Optionally removes
    keys from the dictionary.

    Args:
        params (dict): Dictionary to hash
        remove_keys (list[str]): List of keys to omit while hashing

    Returns:
        tuple(str, str): Uri string and versioned hash
    """
    remove_keys = remove_keys or []
    local_dict = subset_dict(params, remove_keys=remove_keys)
    uri = uri_string_from_dict(local_dict)
    query_hash = hash_from_uri_string(uri)
    return (uri, query_hash)


def hash_from_dict(input: dict) -> str:
    """Creates a deterministic hash from a dictionary

    Args:
        input (dict): Dictionary to hash

    Returns:
        str: The deterministic hash
    """
    return hash_from_uri_string(uri_string_from_dict(input))


def hash_from_uri_string(uri_string: str) -> str:
    """Hashes a string for use with SERP components in the ecosystem

    Args:
        uri_string (str): String to hash

    Returns:
        str: Versioned hash of the passed uri string
    """

    hasher = hashlib.new("sha1", usedforsecurity=False)  # noqa: S324
    hasher.update(uri_string.encode("utf-8"))
    return f"{HASH_VERSION}_{hasher.hexdigest()}"


def uri_string_from_dict(input: dict) -> str:
    """Given a dictionary, creates a deterministic string
    of sorted keys and values, in uri-string format.

    Args:
        input (dict): The dictionary to convert

    Returns:
        str: Uri-string representation of key-value pairs
    """

    keys = sorted(input.keys())
    pre_hash = [f"{k}={input[k]}" for k in keys]
    return "&".join(pre_hash)


def subset_dict(input: dict, remove_keys: list = None) -> dict:
    """Returns a copy of the input dictionary with listed
    keys removed.

    Args:
        input (str): Dictionary to subset
        remove_keys (list[str]): List of keys to omit

    Returns:
        dict: Resulting dictionary
    """
    remove_keys = remove_keys or []
    output = input.copy()
    [output.pop(k) for k in remove_keys]
    return output


def partitioned_hash(qh: str) -> str:
    """Partions the query hash for S3 storage to avoid too many files in a single directory/prefix"""
    return f"{qh[0:2]}/{qh[3:4]}/{qh[4:5]}/{qh[5:6]}/{qh}"
