from typing import Optional
from retrieval.relationship_search import find_relationships as run_find_relationships


def find_relationships(
    symbol_name: str,
    direction: str = "both",
    repo_path: Optional[str] = None
):
    """
    Find relationships involving a function, method, or class.
    """
    return run_find_relationships(symbol_name=symbol_name, direction=direction, repo_path=repo_path)
