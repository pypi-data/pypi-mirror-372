from typing import Any, List, Optional, Sequence, Set

from unpact.constants import MAPPING_TYPES, SEQUENCE_TYPES
from unpact.types import ColumnSpec
from unpact.types.values import MappingValue, UnpackableData

__all__ = ("infer_columns",)


def __remove_redundant_paths(keys: List[str]) -> List[str]:
    # Sort the keys
    sorted_keys = sorted(keys)

    # List to hold the final set of keys
    final_keys = []

    # Iterate through the sorted list of keys
    for i in range(len(sorted_keys)):
        # Ensure this isn't the last element to avoid IndexError
        if i + 1 < len(sorted_keys):
            # Check if the next key starts with the current key followed by a dot (indicating a parent-child relationship)
            if not sorted_keys[i + 1].startswith(sorted_keys[i] + "."):
                final_keys.append(sorted_keys[i])
        else:
            # Always add the last key since it can't be a prefix of any key that follows
            final_keys.append(sorted_keys[i])

    return final_keys


def __get_keys_nested_dict(dictionary: MappingValue, parent_key: str = "", sep: str = ".") -> Set[str]:
    """
    Get all keys in a nested dictionary in dot-delimited format.

    Args:
        dictionary (dict): The nested dictionary.
        parent_key (str): The parent key to append for recursive calls (default is an empty string).
        sep (str): The separator for joining keys (default is dot ".").

    Returns:
        set: A set of keys in dot-delimited format.
    """
    keys: List[str] = []
    for key, value in dictionary.items():
        full_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, MAPPING_TYPES):
            keys.extend(__get_keys_nested_dict(value, full_key, sep=sep))
        elif isinstance(value, SEQUENCE_TYPES):
            for _, item in enumerate(value):
                if isinstance(item, MAPPING_TYPES):
                    keys.extend(__get_keys_nested_dict(item, f"{full_key}", sep=sep))
                else:
                    keys.append(f"{full_key}")
        else:
            keys.append(full_key)
    return set(keys)


def __get_keys_from_sample(sample: Sequence[Any]) -> Set[str]:
    keys: Set[str] = set()
    for item in sample:
        keys.update(__get_keys_nested_dict(item))
    return keys


def infer_columns(
    data: UnpackableData, column_defs: List[ColumnSpec], infer_length: Optional[int] = None
) -> List[ColumnSpec]:
    """
    Infers additional column definitions from the provided data and combines them with the given column definitions.
    Args:
        data (UnpackableData): The data from which to infer column definitions. This can be a nested dictionary or a list of dictionaries.
        column_defs (List[ColumnSpec]): A list of predefined column specifications.
        infer_length (Optional[int], optional): The number of samples to use for inferring columns if the data is a list. Defaults to None.
    Returns:
        List[ColumnSpec]: A list of combined column specifications, including both the predefined and inferred columns.
    """

    keys = (
        __get_keys_nested_dict(data)  # type: ignore
        if isinstance(data, MAPPING_TYPES)
        else __get_keys_from_sample(data[:infer_length] if infer_length else data)  # type: ignore
    )
    specified_keys = [c.path for c in column_defs]
    extra_paths = [k for k in keys if k not in specified_keys]
    extra_defs: List[ColumnSpec] = [ColumnSpec(path=k, name=k) for k in extra_paths]
    column_defs = [*column_defs, *extra_defs]
    path_list = [c.path for c in column_defs]
    unique_paths = __remove_redundant_paths(path_list)

    column_defs = [c for c in column_defs if c.path in unique_paths]
    return column_defs
