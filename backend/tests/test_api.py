from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from api.app import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


def test_get_all_repositories(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    response = client.get("/api/repositories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(r["repo_id"] == temp_repo.name for r in data)


def test_get_repository_info_not_found():
    response = client.get("/api/repositories/nonexistent_xyz")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_clone_repository_invalid_url():
    response = client.post("/api/repositories", json={"repo_url": "invalid_url"})
    assert response.status_code == 400
    assert "Invalid repository URL" in response.json()["detail"]


@patch("api.routes.repositories.clone_repository")
@patch("api.routes.repositories.build_index")
def test_clone_and_index_repository_success(mock_build_index, mock_clone_repo, temp_repo):
    mock_clone_repo.return_value = str(temp_repo)
    mock_build_index.return_value = []

    response = client.post("/api/repositories", json={"repo_url": "https://github.com/test/repo"})
    assert response.status_code == 201
    data = response.json()
    assert data["repo_id"] == temp_repo.name


def test_get_repository_info_success(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    response = client.get(f"/api/repositories/{temp_repo.name}")
    assert response.status_code == 200
    data = response.json()
    assert data["repo_id"] == temp_repo.name


def test_get_repository_structure_success(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    response = client.get(f"/api/repositories/{temp_repo.name}/structure")
    assert response.status_code == 200
    data = response.json()
    assert "src/" in data["structure"]


def test_get_repository_file_content_success(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    response = client.get(f"/api/repositories/{temp_repo.name}/file?path=main.py")
    assert response.status_code == 200
    data = response.json()
    assert data["repo_id"] == temp_repo.name
    assert "entry_point" in data["content"]



def test_search_codebase_endpoint(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    search_payload = {
        "query": "Processor class",
        "symbol_name": "Processor",
        "limit": 5
    }
    response = client.post(f"/api/repositories/{temp_repo.name}/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["repo_id"] == temp_repo.name
    assert "results" in data


def test_symbol_endpoint(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    with patch("api.routes.symbols.find_symbol") as mock_find_symbol:
        mock_find_symbol.return_value = [{"name": "Processor", "type": "class"}]
        response = client.get(f"/api/repositories/{temp_repo.name}/symbols/Processor")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol_name"] == "Processor"
        assert data["total_matches"] == 1


def test_relationship_endpoint(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    with patch("api.routes.relationships.find_relationships") as mock_find_rel:
        mock_find_rel.return_value = {
            "outgoing": [{"caller": "run", "callee": "validate"}],
            "incoming": []
        }
        response = client.get(f"/api/repositories/{temp_repo.name}/relationships/run?direction=both")
        assert response.status_code == 200
        data = response.json()
        assert data["symbol_name"] == "run"
        assert len(data["outgoing"]) == 1


@patch("api.routes.ask.run_agent")
def test_ask_endpoint_success(mock_run_agent, temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    mock_run_agent.return_value = {
        "status": "completed",
        "answer": "Processor.run() validates and executes.",
        "state": {"iterations": 1},
        "evidence": []
    }

    response = client.post(f"/api/repositories/{temp_repo.name}/ask", json={"question": "What does run do?"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["answer"] == "Processor.run() validates and executes."


def test_ask_endpoint_empty_question(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    response = client.post(f"/api/repositories/{temp_repo.name}/ask", json={"question": "   "})
    assert response.status_code == 400


@patch("api.routes.ask.run_agent")
def test_ask_endpoint_quota_exhausted(mock_run_agent, temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    mock_run_agent.return_value = {
        "status": "quota_exhausted",
        "error": "Gemini LLM quota exhausted (429)."
    }

    response = client.post(f"/api/repositories/{temp_repo.name}/ask", json={"question": "What does run do?"})
    assert response.status_code == 429
    assert "quota" in response.json()["detail"].lower()


def test_delete_repository_success(temp_repo, monkeypatch):
    monkeypatch.setattr("api.repository_manager.REPOS_BASE_DIR", temp_repo.parent)
    response = client.delete(f"/api/repositories/{temp_repo.name}")
    assert response.status_code == 200
    data = response.json()
    assert data["repo_id"] == temp_repo.name
    assert not temp_repo.exists()

