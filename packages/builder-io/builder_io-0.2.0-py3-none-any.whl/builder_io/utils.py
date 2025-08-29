"""Utils."""

__all__: tuple[str, ...] = ("JSON", "get_paths", "strip_keys")

import re

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


def get_paths(
    data: JSON,
    value_regex: set[str],
    *,
    sep: str = "/",
) -> dict[str, str | None]:
    """Return a dict of paths to values matching any regex in `value_regex`.

    The values are what was captured by the RegEx, if anything.

    Examples:
    --------
    >>> get_paths({"a": {"b": "target"}, "c": ["no", "target"]}, {"target"})
    {'a/b': None, 'c/1': None}
    """
    paths: dict[str, str | None] = {}

    def _get_paths(d: JSON, current_path: str) -> None:
        if isinstance(d, dict):
            for k, v in d.items():
                new_path = f"{current_path}{sep}{k}" if current_path else k
                _get_paths(v, new_path)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                new_path = f"{current_path}{sep}{i}" if current_path else str(i)
                _get_paths(item, new_path)
        elif isinstance(d, str):
            for pattern in value_regex:
                match = re.fullmatch(pattern, d)
                if match:
                    paths[current_path] = match[1] if match.groups() else None
                    return

    _get_paths(data, "")
    return paths
