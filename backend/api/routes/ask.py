from fastapi import APIRouter, HTTPException, status

from api.models import AskRequest, AskResponse
from api.repository_manager import get_repo_path
from agent import run_agent
from utils.errors import RepositoryNotFoundError, LLMQuotaExhaustedError

router = APIRouter(prefix="/api/repositories", tags=["Ask Agent"])


@router.post("/{repo_id}/ask", response_model=AskResponse)
def ask_codebase_mentor(repo_id: str, payload: AskRequest):
    """
    Main investigation endpoint: Delegates the user's question to the AgentController.
    Returns the evidence-grounded answer, evidence list, state summary, and status.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    try:
        repo_path = get_repo_path(repo_id)
        result = run_agent(question=payload.question, repo_path=str(repo_path))

        status_str = result.get("status", "completed")
        if status_str == "quota_exhausted":
            # Return HTTP 429 status for quota exhaustion
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=result.get("error", "LLM Quota exhausted. Unable to proceed with LLM calls.")
            )
        elif status_str == "error" or result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "AI Agent investigation failed.")
            )

        raw_answer = result.get("answer")
        answer_text = None
        if isinstance(raw_answer, list):
            answer_text = "\n".join(
                [item.get("text", str(item)) if isinstance(item, dict) else str(item) for item in raw_answer]
            )
        elif isinstance(raw_answer, dict):
            answer_text = raw_answer.get("text", str(raw_answer))
        elif raw_answer is not None:
            answer_text = str(raw_answer)

        return AskResponse(
            repo_id=repo_id,
            question=payload.question,
            status=status_str,
            answer=answer_text,
            warning=result.get("warning"),
            error=result.get("error"),
            state=result.get("state", {}),
            evidence=result.get("evidence", [])
        )
    except RepositoryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )
