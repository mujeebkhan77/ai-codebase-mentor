import json
from typing import Optional
from retrieval.symbol_search import find_symbol as run_find_symbol


def find_symbol(
    name: str,
    repo_path: Optional[str] = None,
    symbol_type: Optional[str] = None,
    class_name: Optional[str] = None
):
    """
    Find an exact class, function, or method by name.
    """

    symbols = run_find_symbol(name=name, repo_path=repo_path)
    matches = []

    for symbol in symbols:
        if symbol_type and symbol.get("type") != symbol_type:
            continue
        if class_name and symbol.get("class") != class_name:
            continue
        matches.append(symbol)

    return json.dumps(matches, indent=2)