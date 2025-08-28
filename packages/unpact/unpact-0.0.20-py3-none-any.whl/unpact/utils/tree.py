from typing import Any, Dict, Sequence, Union

from unpact.classes.tree import Tree
from unpact.types import ColumnDef, ColumnSpec

__all__ = ("create_tree",)


def _load_tree(tree_dict: Dict, path: str, parent: Union[Tree, None] = None, root_name: str = "root") -> Tree:
    if parent is None:
        tree = Tree(parent, path=root_name)
    else:
        tree = Tree(parent, path=path)

    if isinstance(tree_dict, dict):
        for k, v in tree_dict.items():
            child = _load_tree(v, k, tree)
            tree.add_child(child)

    return tree


def _set(obj: Dict, path: str, value: Any) -> None:
    *split_path, last = path.split(".")
    for bit in split_path:
        new_obj = obj.setdefault(bit, {})
        if new_obj is not None:
            obj = obj.setdefault(bit, {})
        if new_obj is None:
            obj[bit] = {}
    try:
        obj[last] = value
    except Exception as e:
        raise e


def create_tree(columns: Sequence[ColumnDef]) -> Tree:
    """
    Creates a tree structure from a sequence of column definitions.
    Args:
        paths (Sequence[ColumnDef]): A sequence of column definitions.
    Returns:
        Tree: The constructed tree with the specified column definitions.
    The function performs the following steps:
    1. Converts each column definition into a ColumnSpec object.
    2. Initializes an empty dictionary to represent the tree structure.
    3. Populates the dictionary with paths from the column definitions.
    4. Loads the tree from the dictionary.
    5. Sets the tree specification and formatter properties for each child node in the tree.
    """

    column_defs = [ColumnSpec.from_def(path) for path in columns]

    tree_dict: Dict[str, Any] = {}
    for col_def in column_defs:
        _set(tree_dict, col_def.path, None)
    tree = _load_tree(tree_dict, "None", parent=None)

    for col_def in column_defs:
        child = tree.get_child(col_def.path)
        child.set_tree_spec(col_def)

    return tree
