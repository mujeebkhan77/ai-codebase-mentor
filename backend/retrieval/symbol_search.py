import json
from pathlib import Path
from typing import Optional
from retrieval.code_search import is_file_in_repo


def find_symbol(name: str, repo_path: Optional[str] = None):
    """
    Find an exact class, function, or method by name.
    """

    index_path = Path("symbol_index.json")
    if not index_path.exists():
        return []

    with open(
        index_path,
        "r",
        encoding="utf-8"
    ) as file:
        symbols = json.load(file)

    results = []

    for symbol in symbols:
        sym_file = symbol.get("file", "")
        if repo_path and not is_file_in_repo(sym_file, repo_path):
            continue

        if symbol["name"].lower() == name.lower():
            results.append({
                "name": symbol["name"],
                "type": symbol["type"],
                "class": symbol.get("class"),
                "file": sym_file,
                "start_line": symbol["start_line"],
                "end_line": symbol["end_line"]
            })

    return results