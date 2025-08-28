from typing import Any, Callable, Protocol, Union, runtime_checkable

__all__ = ("ColumnFormatter",)


@runtime_checkable
class IndexFormatter(Protocol):
    def __call__(self, data: Any, index: int = ...):
        ...  # pragma: no cover


@runtime_checkable
class RootIndexFormatter(Protocol):
    def __call__(self, data: Any, index: int = ..., root: dict = ...):
        ...  # pragma: no cover


@runtime_checkable
class RootFormatter(Protocol):
    def __call__(self, data: Any, root: dict = ...):
        ...  # pragma: no cover


ColumnFormatter = Union[
    RootIndexFormatter,
    IndexFormatter,
    RootFormatter,
    Callable[[Any], Any],
    Callable[[Any, int], Any],
    Callable[[Any, dict], Any],
    Callable[[Any, int, dict], Any],
    Callable[[Any, dict, int], Any],
]
