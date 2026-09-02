import pytest
from pathlib import Path
from retrieval.engine import RetrievalEngine
from agent.controller import run_agent
from indexing.index_repository import index_repository

RAG_REPO_PATH = Path("repositories/universal-rag-chatbot").resolve()
FLASK_REPO_PATH = Path("repositories/flask").resolve()


def test_retrieval_engine_repository_isolation():
    """Verify RetrievalEngine search against universal-rag-chatbot NEVER returns flask evidence."""
    if RAG_REPO_PATH.exists():
        index_repository(RAG_REPO_PATH)
    if FLASK_REPO_PATH.exists():
        index_repository(FLASK_REPO_PATH)

    engine = RetrievalEngine(repo_path=str(RAG_REPO_PATH))

    # Query for Flask-specific symbols and files while targeting RAG repo
    results = engine.search("Flask dispatch_request app.py route", limit=15)

    for item in results:
        file_path = str(item.get("file", "")).replace("\\", "/")
        assert "repositories/flask" not in file_path.lower(), (
            f"Cross-repository pollution detected! Item file '{file_path}' belongs to flask repo."
        )
        if file_path:
            assert "universal-rag-chatbot" in file_path.lower() or "repositories/universal-rag-chatbot" in file_path.lower()


def test_agent_investigation_repository_isolation():
    """Verify run_agent against universal-rag-chatbot NEVER returns flask evidence."""
    if not RAG_REPO_PATH.exists():
        pytest.skip("universal-rag-chatbot repository not present.")

    question = "How does this application handle requests and dispatch routing?"
    res = run_agent(question, repo_path=str(RAG_REPO_PATH))

    evidence = res.get("evidence", [])
    for item in evidence:
        file_path = str(item.get("file", "")).replace("\\", "/")
        assert "repositories/flask" not in file_path.lower(), (
            f"Cross-repository evidence pollution detected! Evidence file '{file_path}' belongs to flask."
        )
