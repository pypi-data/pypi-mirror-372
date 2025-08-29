import typing as t

SIZE_UNIT: t.Final = "B"
DEFAULT_PRECISION: t.Final = 2


def size(size_bytes: int | float, precision: int = DEFAULT_PRECISION) -> str:
    """
    Converts the given size in bytes into a human-friendly string representation.

    Args:
        size_bytes (int or float): The size in bytes to convert.
        precision (int, optional): The number of decimal places to round the
            result to. Defaults to 2.

    Returns:
        str: A human-friendly string representation of the given size,
            e.g. 4.00 B, 1.00 KiB, 1.23 MiB, etc.
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.{precision}f} {unit}{SIZE_UNIT}"
        size_bytes /= 1024.0
    return f"{size_bytes:.{precision}f} Yi{SIZE_UNIT}"
