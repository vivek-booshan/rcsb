import warnings
from typing import Iterable, Optional

def unwrap_query(
    query: dict[str, dict|list],
    path: Iterable[str], 
    default: Optional[str] = None,
    strict: bool = False
) -> Optional[any]:
    """Unwrap the results from a submitted query (nested dictionary)."""
    current = query
    if current is None:
        return default

    for depth, key in enumerate(path):
        if isinstance(current, list):
            if len(current) == 1:
                current = current[0]
            elif len(current) > 1:
                if strict:
                    raise ValueError(
                        f"Ambiguous data at depth {depth}: List contains multiple items "
                        f"but unwrap_query expected a single object or scalar."
                    )
                else:
                    warnings.warn(
                        f"Ambiguous data at depth {depth} for key '{key}': "
                        f"List contains {len(current)} items. Defaulting to the first item. "
                        f"Set strict=True to raise an error instead.",
                        UserWarning,
                        stacklevel=2
                    )
                    current = current[0]
            elif len(current) == 0:
                return default

        try:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and isinstance(key, int):
                current = current[key]
            else:
                return default
        except (IndexError, AttributeError, TypeError):
            return default

        if current is None:
            return default

    return current
