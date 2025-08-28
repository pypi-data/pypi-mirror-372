from typing import Any, Mapping, Sequence, Union

__all__ = ("UnpackableData", "MappingSequence", "MappingValue")

MappingValue = Mapping[str, Any]

MappingSequence = Sequence[MappingValue]

SequentialValue = Union[list, tuple, set]

UnpackableData = Union[MappingValue, MappingSequence]
