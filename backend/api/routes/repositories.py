from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, Query, status

from api.models import (
    CloneRepoRequest,
    RepoInfoResponse,
    RepoStructureResponse,
    RepoFileResponse,
    DeleteRepoResponse
)
from api.repository_manager import (
    get_repo_path,
    load_repo_manifest,
    list_repositories,
    delete_repository,
    sanitize_repo_id
)
from tools import clone_repository, get_repository_structure, read_file
from indexing.build_index import build_index
from utils.errors import RepositoryNotFoundError

router = APIRouter(prefix="/api/repositories", tags=["Repositories"])


@router.get("", response_model=List[RepoInfoResponse])
def get_all_repositories():
    """
    List all locally available indexed repositories.
    """
    try:
        repos = list_repositories()
        return [
            RepoInfoResponse(
                repo_id=r["repo_id"],
                repo_path=r["repo_path"],
                manifest=r["manifest"]
            )
            for r in repos
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list repositories: {str(e)}"
        )


@router.post("", response_model=RepoInfoResponse, status_code=status.HTTP_201_CREATED)
def clone_and_index_repository(payload: CloneRepoRequest):
    """
    Clone a GitHub repository (shallow clone) and build its symbol/relationship index.
    """
    if not payload.repo_url or not payload.repo_url.startswith(("http://", "https://", "git@")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid repository URL provided."
        )

    try:
        # Clone repository
        clone_path_str = clone_repository(payload.repo_url)
        clone_path = Path(clone_path_str).resolve()
        repo_id = clone_path.name

        # Build index and manifest
        build_index(str(clone_path))
        manifest = load_repo_manifest(clone_path)

        return RepoInfoResponse(
            repo_id=repo_id,
            repo_path=str(clone_path),
            manifest=manifest
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clone or index repository: {str(e)}"
        )


@router.get("/{repo_id}", response_model=RepoInfoResponse)
def get_repository_info(repo_id: str):
    """
    Get repository information and manifest for repo_id.
    """
    try:
        repo_path = get_repo_path(repo_id)
        manifest = load_repo_manifest(repo_path)
        return RepoInfoResponse(
            repo_id=repo_id,
            repo_path=str(repo_path),
            manifest=manifest
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{repo_id}", response_model=DeleteRepoResponse)
def delete_indexed_repository(repo_id: str):
    """
    Delete a repository directory and its local indexes from disk.
    """
    try:
        success = delete_repository(repo_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository '{repo_id}' not found."
            )
        return DeleteRepoResponse(
            repo_id=repo_id,
            message=f"Repository '{repo_id}' successfully removed from disk."
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{repo_id}/structure", response_model=RepoStructureResponse)
def get_repository_file_structure(repo_id: str):
    """
    Get repository file tree structure for repo_id.
    """
    try:
        repo_path = get_repo_path(repo_id)
        structure_str = get_repository_structure(str(repo_path))
        return RepoStructureResponse(
            repo_id=repo_id,
            structure=structure_str
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{repo_id}/file", response_model=RepoFileResponse)
def get_repository_file_content(repo_id: str, path: str = Query(..., description="Relative or absolute file path")):
    """
    Get raw content of a file within repo_id.
    """
    try:
        repo_path = get_repo_path(repo_id)
        rel_path = Path(path)
        
        # If relative, join with repo_path
        if rel_path.is_absolute():
            full_path = rel_path.resolve()
        else:
            full_path = (repo_path / rel_path).resolve()

        # Prevent path traversal outside repo_path
        try:
            full_path.relative_to(repo_path)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access denied: file path outside repository.")

        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File '{path}' not found.")

        content = read_file(str(full_path))
        if isinstance(content, dict) and "error" in content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=content["error"])

        return RepoFileResponse(
            repo_id=repo_id,
            path=path,
            content=str(content)
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to read file: {str(e)}")
