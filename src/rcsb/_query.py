from typing import Iterable, Optional
def unwrap_query(
    query, # graphql query  
    path: Iterable[str], 
    default: Optional[str] = None,
    strict: bool = False
) -> str:
    current = query
    if current is None:
        return default

    for depth, key in enumerate(path):
        if isinstance(current, list):
            if len(current) == 1:
                current = current[0]
            elif len(current) > 1 and strict:
                raise ValueError(
                    f"Ambiguous data at depth {depth}: List contains multiple items "
                    f"but resolve_unwrapped expected a single object or scalar."
                )
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
