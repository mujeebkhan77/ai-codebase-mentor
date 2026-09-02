import os
import re
import json
import shutil
import stat
from pathlib import Path
from typing import Dict, Any, Optional, List

from utils.errors import RepositoryNotFoundError


REPOS_BASE_DIR = Path("repositories").resolve()


def sanitize_repo_id(repo_id: str) -> str:
    """Sanitize and validate repository ID string to prevent path traversal."""
    sanitized = re.sub(r"[^a-zA-Z0-9_\-]", "", repo_id)
    if not sanitized or sanitized.startswith("."):
        raise ValueError(f"Invalid repository ID: '{repo_id}'")
    return sanitized


def get_repo_path(repo_id: str) -> Path:
    """
    Resolve and validate repository path on disk under REPOS_BASE_DIR.
    Raises RepositoryNotFoundError if repository directory does not exist.
    """
    clean_id = sanitize_repo_id(repo_id)
    target_path = (REPOS_BASE_DIR / clean_id).resolve()

    # Prevent escaping REPOS_BASE_DIR
    try:
        target_path.relative_to(REPOS_BASE_DIR)
    except ValueError:
        raise ValueError(f"Access denied for repository path: {repo_id}")

    if not target_path.exists() or not target_path.is_dir():
        raise RepositoryNotFoundError(f"Repository '{repo_id}' not found at {target_path}")

    return target_path


def load_repo_manifest(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Load repository_manifest.json from root or repository directory if present."""
    manifest_paths = [
        repo_path / "repository_manifest.json",
        Path("repository_manifest.json")
    ]
    for mp in manifest_paths:
        if mp.exists():
            try:
                with open(mp, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return None


def list_repositories() -> List[Dict[str, Any]]:
    """List all available indexed repository directories in REPOS_BASE_DIR."""
    if not REPOS_BASE_DIR.exists():
        return []

    repos = []
    for item in REPOS_BASE_DIR.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            manifest = load_repo_manifest(item)
            repos.append({
                "repo_id": item.name,
                "repo_path": str(item),
                "manifest": manifest
            })
    return repos


def _remove_readonly(func, path, exc_info):
    """Handler to clear read-only flag on Windows files during shutil.rmtree."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def delete_repository(repo_id: str) -> bool:
    """Safely delete repository directory from disk."""
    target_path = get_repo_path(repo_id)
    if target_path.exists() and target_path.is_dir():
        shutil.rmtree(target_path, onerror=_remove_readonly)
        return True
    return False

