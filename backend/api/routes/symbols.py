from fastapi import APIRouter, HTTPException, status

from api.models import SymbolResponse
from api.repository_manager import get_repo_path
from retrieval.symbol_search import find_symbol
from utils.errors import RepositoryNotFoundError

router = APIRouter(prefix="/api/repositories", tags=["Symbols"])


@router.get("/{repo_id}/symbols/{name}", response_model=SymbolResponse)
def get_symbol_by_name(repo_id: str, name: str):
    """
    Find exact class, function, or method location details by symbol name.
    """
    try:
        get_repo_path(repo_id)  # Validate repo existence
        matches = find_symbol(name)

        return SymbolResponse(
            repo_id=repo_id,
            symbol_name=name,
            total_matches=len(matches),
            symbols=matches
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symbol lookup failed: {str(e)}"
        )
