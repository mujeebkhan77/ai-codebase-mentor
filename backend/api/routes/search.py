from fastapi import APIRouter, HTTPException, status

from api.models import SearchRequest, SearchResponse
from api.repository_manager import get_repo_path
from retrieval.engine import RetrievalEngine
from utils.errors import RepositoryNotFoundError

router = APIRouter(prefix="/api/repositories", tags=["Search"])


@router.post("/{repo_id}/search", response_model=SearchResponse)
def search_codebase(repo_id: str, payload: SearchRequest):
    """
    Search the repository using the multi-strategy RetrievalEngine.
    """
    try:
        repo_path = get_repo_path(repo_id)
        engine = RetrievalEngine(repo_path=str(repo_path))

        results = engine.search(
            query=payload.query,
            symbol_name=payload.symbol_name,
            keywords=payload.keywords,
            repo_path=str(repo_path),
            limit=payload.limit,
            strategies=payload.strategies
        )

        return SearchResponse(
            repo_id=repo_id,
            query=payload.query,
            total_results=len(results),
            results=results
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )
