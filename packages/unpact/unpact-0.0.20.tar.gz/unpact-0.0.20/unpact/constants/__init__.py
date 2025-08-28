from collections.abc import Mapping

TERMINAL_TYPES = (bool, bytes, complex, float, int, str)
SEQUENCE_TYPES = (list, tuple, set)
MAPPING_TYPES = (Mapping,)


__all__ = ("TERMINAL_TYPES", "SEQUENCE_TYPES", "MAPPING_TYPES")
