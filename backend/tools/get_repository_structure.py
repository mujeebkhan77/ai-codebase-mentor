import os
from pathlib import Path
from utils.caching import global_cache


def get_repository_structure(repo_path: str):
    """
    Analyze the structure of a repository by listing important files and folders.

    Use this tool when you need to:
    - understand the overall organization of a codebase
    - discover where different parts of a project are located
    - find likely locations of source code, documentation, or configuration files
    - get an overview before searching or reading specific files
    """
    path = Path(repo_path)
    if not path.exists():
        return f"Error: Repository path '{repo_path}' does not exist."

    # Check cache
    cache_key = str(path.resolve())
    cached_structure = global_cache.get("structure", cache_key)
    if cached_structure:
        return cached_structure

    structure = []
    ignore_dirs = {".git", "__pycache__", ".venv", "node_modules", "chroma_db"}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        rel_root = os.path.relpath(root, repo_path)
        level = 0 if rel_root == "." else rel_root.count(os.sep) + 1

        if level > 3:
            continue

        indent = "    " * level
        dir_name = os.path.basename(root) if rel_root != "." else os.path.basename(os.path.abspath(repo_path))
        structure.append(f"{indent}{dir_name}/")

        for file in files[:10]:
            structure.append(f"{indent}    {file}")

    result = "\n".join(structure)
    global_cache.set("structure", cache_key, result)
    return result
