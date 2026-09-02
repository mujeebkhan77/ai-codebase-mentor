import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Any


def generate_manifest(
    repository_path: str | Path,
    symbols: List[Dict[str, Any]] = None,
    relationships: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a lightweight, deterministic repository manifest.
    Does NOT use LLMs. Uses file inspection and symbol/relationship data.
    """
    repo_path = Path(repository_path).resolve()
    repo_name = repo_path.name

    if symbols is None:
        symbols = []
    if relationships is None:
        relationships = []

    # File extensions and language counts
    extension_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".md": "markdown",
    }

    language_counter = Counter()
    source_dirs = set()
    test_dirs = set()
    config_files = []
    entry_points = []
    total_files = 0

    known_entry_filenames = {
        "main.py", "__main__.py", "app.py", "cli.py", "wsgi.py",
        "index.js", "server.js", "main.go", "Main.java"
    }

    known_config_filenames = {
        "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
        "Pipfile", "poetry.lock", "package.json", "Cargo.toml",
        "Dockerfile", "docker-compose.yml", ".env.example"
    }

    ignore_dirs = {".git", "__pycache__", ".venv", "node_modules", "chroma_db"}

    for path in repo_path.rglob("*"):
        if any(part in ignore_dirs for part in path.parts):
            continue

        if path.is_file():
            total_files += 1
            ext = path.suffix.lower()
            if ext in extension_map:
                language_counter[extension_map[ext]] += 1

            rel_path = path.relative_to(repo_path)
            parts = rel_path.parts

            if len(parts) > 1:
                top_dir = parts[0]
                if top_dir.lower() in ("test", "tests", "testing"):
                    test_dirs.add(top_dir)
                elif top_dir.lower() in ("src", "lib", repo_name.lower()):
                    source_dirs.add(top_dir)

            if path.name in known_config_filenames:
                config_files.append(str(rel_path).replace("\\", "/"))

            if path.name in known_entry_filenames:
                entry_points.append(str(rel_path).replace("\\", "/"))

    # Filter symbols and relationships strictly belonging to this repository
    from retrieval.code_search import is_file_in_repo
    symbols = [s for s in symbols if is_file_in_repo(s.get("file", ""), repo_path)]
    relationships = [r for r in relationships if is_file_in_repo(r.get("file") or r.get("target_file") or "", repo_path)]

    # Symbol statistics
    classes = [s for s in symbols if s.get("type") == "class"]
    functions = [s for s in symbols if s.get("type") == "function"]
    methods = [s for s in symbols if s.get("type") == "method"]

    # Relationship statistics
    callee_counts = Counter(r.get("callee") for r in relationships if r.get("callee"))
    top_called = [{"symbol": sym, "call_count": count} for sym, count in callee_counts.most_common(10)]

    manifest = {
        "repository_name": repo_name,
        "total_files": total_files,
        "languages": dict(language_counter),
        "source_directories": sorted(list(source_dirs)),
        "test_directories": sorted(list(test_dirs)),
        "config_files": sorted(config_files),
        "entry_points": sorted(entry_points),
        "symbols_summary": {
            "total_symbols": len(symbols),
            "classes_count": len(classes),
            "functions_count": len(functions),
            "methods_count": len(methods),
        },
        "relationships_summary": {
            "total_relationships": len(relationships),
            "top_called_symbols": top_called
        }
    }

    return manifest


def save_manifest(manifest: Dict[str, Any], output_path: str | Path = "repository_manifest.json") -> None:
    path = Path(output_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
