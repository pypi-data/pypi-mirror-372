import typing as t
from collections.abc import Sequence
from functools import partial

T = t.TypeVar("T")
K = t.TypeVar("K")

DEFAULT_ID_ATTR_NAME: t.Final[str] = "id"

#: List of values that are considered empty
EMPTY_VALUES: t.Final[list[t.Any]] = ["", None, [], {}]


def chunker(seq: Sequence[T], size: int) -> list[Sequence[T]]:
    """Splits provided iterable into list of chunks of given size

    Args:
        seq: iterable to split
        size: chunk size

    Returns:
        list of chunks
    """
    return [seq[pos : pos + size] for pos in range(0, len(seq), size)]


@t.overload
def idfy(
    obj: dict[t.Any, t.Any], id_field_name: str = DEFAULT_ID_ATTR_NAME
) -> dict[t.Any, dict[t.Any, t.Any]]: ...


@t.overload
def idfy(obj: list[T], id_field_name: str = DEFAULT_ID_ATTR_NAME) -> dict[t.Any, T]: ...


@t.overload
def idfy(obj: set[T], id_field_name: str = DEFAULT_ID_ATTR_NAME) -> dict[t.Any, T]: ...


@t.overload
def idfy(obj: tuple[T, ...], id_field_name: str = DEFAULT_ID_ATTR_NAME) -> dict[t.Any, T]: ...


@t.overload
def idfy(obj: T, id_field_name: str = DEFAULT_ID_ATTR_NAME) -> dict[t.Any, T]: ...


def idfy(
    obj: T | list[T] | set[T] | tuple[T, ...] | dict[t.Any, t.Any],
    id_field_name: str = DEFAULT_ID_ATTR_NAME,
) -> dict[t.Any, T] | dict[t.Any, dict[t.Any, t.Any]]:
    """Converts given object into dict with ``id_field_name`` values as a key
    and actual object as a value.

    If given object is a dict this function uses to get value of
    ``id_field_name`` key. If any other object - looks for ``id_field_name``
    attribute.

    Raises :py:exc:`ValueError` if there's no appropriate id value found.

    Applied recursively if :py:class:`Iterable` is given as an input.

    Args:
        obj (T): object to convert to dictionary
        id_field_name (str): name of the field/attribute to use to get, defaults
            to `"id"`

    Returns:
        dict with ``id_field_name`` values as a key and actual object as a value
    """
    if isinstance(obj, dict):
        try:
            return {obj[id_field_name]: obj}
        except KeyError as err:
            raise ValueError(f"Can't get '{id_field_name}' key from {obj} dict") from err
    if isinstance(obj, (list, set, tuple, t.Generator)):
        return {k: v for d in obj for k, v in idfy(d, id_field_name).items()}
    if hasattr(obj, id_field_name):
        return {getattr(obj, id_field_name): obj}
    raise ValueError(f"Can't get {id_field_name} attribute from {obj}")


@t.overload
def remove_empty_members(
    obj: dict[t.Any, t.Any], empty: list[t.Any] | None = None
) -> dict[t.Any, t.Any] | None: ...


@t.overload
def remove_empty_members(
    obj: list[t.Any], empty: list[t.Any] | None = None
) -> list[t.Any] | None: ...


@t.overload
def remove_empty_members(obj: T, empty: list[t.Any] | None = None) -> T | None: ...


def remove_empty_members(obj: T, empty: list[t.Any] | None = None) -> T | None:
    """Removes empty members from given object.

    Recursively goes through the given object and removes its members that are
    considered empty. If given object is a dict, removes keys that have empty
    values. If given object is a list removes empty items from it.

    Args:
        obj: object to remove empty members from
        empty: list of values that are considered empty. If not given, defaults to
            :const:`EMPTY_VALUES`

    Returns:
        object with empty members removed, or None if the object itself is empty
    """
    empty = empty or EMPTY_VALUES
    cleaners: dict[type, t.Callable[[t.Any, list[t.Any]], t.Any]]
    cleaners = {
        dict: _remove_empty_members_from_dict,
        list: _remove_empty_members_from_list,
    }
    if (cleaner := cleaners.get(type(obj))) is not None:
        obj = cleaner(obj, empty)
    if obj in empty:
        return None
    return obj


def _remove_empty_members_from_dict(
    obj: dict[t.Any, t.Any], empty: list[t.Any]
) -> dict[t.Any, t.Any]:
    for key in list(obj.keys()):
        obj[key] = remove_empty_members(obj[key], empty)
        if obj[key] is None:
            del obj[key]
    return obj


def _remove_empty_members_from_list(obj: list[t.Any], empty: list[t.Any]) -> list[t.Any]:
    return list(
        filter(lambda x: x not in empty, map(partial(remove_empty_members, empty=empty), obj))
    )
