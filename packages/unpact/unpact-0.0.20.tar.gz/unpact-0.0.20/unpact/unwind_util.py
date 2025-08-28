from typing import Any, Dict, List, Optional, Sequence

from unpact.classes.unpacker import Unpacker
from unpact.types import ColumnDef
from unpact.types.values import UnpackableData

__all__ = ["unwind"]


def unwind(
    data: UnpackableData,
    columns: Sequence[ColumnDef],
    allow_extra: bool = False,
    infer_length: Optional[int] = 10,
) -> List[Dict[str, Any]]:
    unpacker = Unpacker(columns=columns, allow_extra=allow_extra, infer_length=infer_length)

    return unpacker.apply(data)
