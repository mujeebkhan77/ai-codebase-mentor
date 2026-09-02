import json
from pathlib import Path
from typing import Optional
from retrieval.code_search import is_file_in_repo


def load_relationship_index():
    """
    Load the resolved relationship index created during repository indexing.
    """

    relationship_index_path = Path(
        "relationship_index.json"
    )

    if not relationship_index_path.exists():
        return []

    with open(
        relationship_index_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def find_relationships(
    symbol_name: str,
    direction: str = "both",
    repo_path: Optional[str] = None
):
    """
    Find relationships involving a function, method, or class.
    """

    relationships = load_relationship_index()

    symbol_name = symbol_name.strip()

    if not symbol_name:
        return {
            "symbol": symbol_name,
            "relationships": []
        }

    outgoing = []
    incoming = []

    for relationship in relationships:
        rel_file = relationship.get("file") or relationship.get("target_file")
        if repo_path and not is_file_in_repo(rel_file, repo_path):
            continue

        caller = relationship.get("caller")
        callee = relationship.get("callee")

        if caller == symbol_name:
            outgoing.append(relationship)

        if callee == symbol_name:
            incoming.append(relationship)

    result = {
        "symbol": symbol_name,
        "direction": direction,
        "outgoing": [],
        "incoming": []
    }

    if direction in {"outgoing", "both"}:
        result["outgoing"] = outgoing

    if direction in {"incoming", "both"}:
        result["incoming"] = incoming

    return result