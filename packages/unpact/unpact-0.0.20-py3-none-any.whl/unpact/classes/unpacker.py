import itertools
from typing import Any, Dict, List, Optional, Sequence, Union

from unpact.classes.tree import Tree
from unpact.constants import MAPPING_TYPES, SEQUENCE_TYPES
from unpact.types import ColumnDef, ColumnSpec, MappingValue, SequentialValue, UnpackableData
from unpact.types.columns import UNSET
from unpact.utils.column_defs import infer_columns
from unpact.utils.tree import create_tree


class Unpacker:
    __slots__ = ["column_defs", "allow_extra", "infer_length", "_tree"]

    def __init__(
        self,
        columns: Optional[Sequence[ColumnDef]] = None,
        allow_extra: bool = False,
        infer_length: Optional[int] = 10,
    ) -> None:
        """
        Initialize an Unpacker instance.
        Args:
            columns (Optional[Sequence[ColumnDef]]): A sequence of column definitions. Defaults to None.
            allow_extra (bool): Flag to allow inferred extra columns. Defaults to False.
            infer_length (Optional[int]): Length to infer, only applies if allow_extra = True. Defaults to 10.
        Attributes:
            allow_extra (bool): Indicates if extra columns are allowed.
            infer_length (Optional[int]): Length to infer.
            column_defs (List[ColumnSpec]): List of column specifications.
            _tree (Optional[Tree]): Internal tree structure. Defaults to None.
        """

        self.allow_extra = allow_extra
        self.infer_length = infer_length
        if not columns:
            self.allow_extra = True
        self.column_defs = [ColumnSpec.from_def(c) for c in columns or []]

        self._tree: Optional[Tree] = None

    def _unwind_list(self, data: SequentialValue, tree: Tree, level_list: List, root_data: MappingValue) -> None:
        for item in data:
            item_output_dict = {}
            item_accum: List[dict] = []
            for child in tree.children:
                value: Union[dict, list] = self._unwind(item, child, root_data)
                if isinstance(value, SEQUENCE_TYPES):
                    if item_accum and len(item_accum) == len(value):  # Handle adjacents
                        item_accum = [{**a, **b} for a, b in zip(item_accum, value)]
                    else:
                        item_accum.extend(value)
                else:
                    item_output_dict.update(value)
            if len(item_accum) > 0:
                level_list.extend([{**item_output_dict, **item} for item in item_accum])
            else:
                level_list.append(item_output_dict)

    def _get_value(self, data: MappingValue, tree: Tree, root_data: MappingValue) -> Any:
        tree_data = data.get(tree.path, UNSET)
        if isinstance(data, SEQUENCE_TYPES):
            return [self._unwind(d, tree, root_data) for d in data]
        if isinstance(tree_data, SEQUENCE_TYPES):
            if tree._partial_formatter:
                return [tree.get_value(x, root_data, idx) for idx, x in enumerate(tree_data)]
            else:
                return [tree.get_value(x) for x in tree_data]  # 0.071
        return tree.get_value(tree_data, root_data)

    def _unwind(
        self, data: MappingValue, tree: Tree, root_data: MappingValue
    ) -> Union[List, List[Dict[str, Any]], Dict[str, Any], dict, List[dict]]:
        if not tree.children:
            return self._get_value(data, tree, root_data)

        level_list: List[dict] = []
        level_dict: dict = {}

        tree_data = data.get(tree.path)
        tree_data = {} if tree_data is None else tree_data
        if isinstance(tree_data, SEQUENCE_TYPES):
            self._unwind_list(tree_data, tree, level_list, root_data)
        else:
            for child in tree.children:
                value = self._unwind(tree_data, child, root_data)
                if isinstance(value, SEQUENCE_TYPES):
                    level_list.extend(value)
                else:
                    level_dict.update(value)

        if len(level_list) == 0:
            return level_dict

        return [{**level_dict, **item} for item in level_list]

    def apply(
        self,
        data: UnpackableData,
    ) -> List[Dict[str, Any]]:
        """
        Apply the unpacking process to the provided data.
        This method processes the input data according to the column definitions
        and the tree structure. If the tree structure is not already created, it
        initializes it based on the column definitions and the data.
        Args:
            data (UnpackableData): The data to be unpacked. It can be a single
                                   mapping or a list of mappings.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the unpacked
                                  data.
        """

        if not self._tree:
            self.column_defs = [ColumnSpec.from_def(c) for c in self.column_defs]
            if self.allow_extra:
                self.column_defs = infer_columns(data, self.column_defs, self.infer_length)

            self._tree = create_tree(self.column_defs)

        def apply_unwind(d: MappingValue, tree: Tree) -> List[Dict[str, Any]]:
            unwound = self._unwind({"root": d}, tree, d)
            if not isinstance(unwound, list):
                return [unwound]
            else:
                return unwound

        if isinstance(data, MAPPING_TYPES):
            return apply_unwind(data, self._tree)  # type: ignore
        else:
            return list(itertools.chain.from_iterable([apply_unwind(d, self._tree) for d in data]))  # type: ignore
