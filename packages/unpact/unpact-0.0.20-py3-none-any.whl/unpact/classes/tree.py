import inspect
import sys
from functools import partial, reduce
from typing import Any, List, Optional, Union

from unpact.types.columns import UNSET
from unpact.types.values import MappingValue

from ..types import ColumnSpec

__all__ = ("Tree",)


class Tree:
    __slots__ = (
        "parent",
        "depth",
        "path",
        "children",
        "tree_spec",
        "_formatter_kwargs",
        "_partial_formatter",
        "name",
        "_value_schema",
    )

    def __init__(self, parent: Optional["Tree"], path: str) -> None:
        self.parent: Union[Tree, None] = parent
        self.depth: int = 0
        if parent and parent.depth is not None:
            self.depth = parent.depth + 1

        self.path: str = path
        self.children: List[Tree] = []
        self.tree_spec: Optional[ColumnSpec] = None
        self._formatter_kwargs: dict = {}
        self.name: Optional[str] = None

        self._partial_formatter: Optional[partial] = None

    def get_value(
        self,
        value: Any,
        root_data: Optional[MappingValue] = None,
        idx: Union[int, None] = None,
    ) -> Any:
        if not self.tree_spec:
            raise ValueError("No tree spec found")

        formatter = self._partial_formatter
        if formatter:
            if "index" in self._formatter_kwargs:
                formatter.keywords["index"] = idx
            if "root" in self._formatter_kwargs:
                formatter.keywords["root"] = root_data

            return formatter(value)

        if value is UNSET:
            if self.tree_spec.default is not UNSET:  # type: ignore
                return {self.name: self.tree_spec.default}  # type: ignore
            return {self.name: None}

        return {self.name: value}

    def add_child(self, child_tree: "Tree") -> None:
        self.children.append(child_tree)

    def get_child(self, path: str) -> "Tree":
        paths = path.split(".")

        def _select_child(tree: "Tree", path: str) -> "Tree":
            return next(filter(lambda p: p.path == path, tree.children), tree)

        child = reduce(lambda tree, path: _select_child(tree, path), paths, self)
        return child

    def __repr__(self) -> str:
        base = f"{self.path}\n"

        for child in self.children:
            sep = "\t" * self.depth
            base += f"{sep}{repr(child)}\n"

        return base

    def _get_name(self, tree_spec: ColumnSpec) -> str:
        if tree_spec.name:
            return tree_spec.name
        return self.path

    def set_tree_spec(self, spec: ColumnSpec) -> None:
        self.tree_spec = spec
        if spec.formatter:
            params = inspect.signature(spec.formatter).parameters
            valid = {"index", "root"}
            for k, v in params.items():
                if k in valid:
                    self._formatter_kwargs[k] = None
            self._partial_formatter = partial(spec.formatter, **self._formatter_kwargs)  # type: ignore

        self.name = sys.intern(self._get_name(spec))
