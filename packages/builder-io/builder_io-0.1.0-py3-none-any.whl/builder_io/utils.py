"""Utils."""

__all__: tuple[str, ...] = ("JSON", "strip_keys")

type JSON = None | bool | int | float | str | list[JSON] | dict[str, JSON]


def strip_keys(data: JSON, keys: set[str]) -> JSON:
    """Return a deep-copied version of `data` (JSON-like) with specified keys removed.

    - Preserves list/dict structure and order.
    - Only the exact key in `keys` is removed (case-sensitive).

    Examples:
    --------
    >>> strip_keys({"id": 1, "name": "A"}, {"id"})
    {'name': 'A'}
    >>> strip_keys([{"id": 1, "x": [{"id": 2}, {"y": 3}]}, {"z": 4}], {"id"})
    [{'x': [{}, {'y': 3}]}, {'z': 4}]
    """
    if isinstance(data, dict):
        return {k: strip_keys(v, keys) for k, v in data.items() if k not in keys}
    if isinstance(data, list):
        return [strip_keys(item, keys) for item in data]
    # primitives (None, bool, int, float, str) pass through
    return data
