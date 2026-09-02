from fastapi import APIRouter, HTTPException, Query, status

from api.models import RelationshipResponse
from api.repository_manager import get_repo_path
from retrieval.relationship_search import find_relationships
from utils.errors import RepositoryNotFoundError

router = APIRouter(prefix="/api/repositories", tags=["Relationships"])


@router.get("/{repo_id}/relationships/{symbol_name}", response_model=RelationshipResponse)
def get_symbol_relationships(
    repo_id: str,
    symbol_name: str,
    direction: str = Query("both", pattern="^(outgoing|incoming|both)$")
):

    """
    Get incoming and/or outgoing call-graph relationships for a symbol.
    """
    try:
        get_repo_path(repo_id)  # Validate repo existence
        rel_data = find_relationships(symbol_name, direction=direction)

        return RelationshipResponse(
            repo_id=repo_id,
            symbol_name=symbol_name,
            direction=direction,
            outgoing=rel_data.get("outgoing", []),
            incoming=rel_data.get("incoming", [])
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Relationship lookup failed: {str(e)}"
        )
