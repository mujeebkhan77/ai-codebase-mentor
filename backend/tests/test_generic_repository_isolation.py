import pytest
from pathlib import Path
from retrieval.code_search import is_file_in_repo
from retrieval.engine import RetrievalEngine
from evidence.manager import EvidenceManager
from agent.controller import run_agent
from indexing.index_repository import index_repository


def test_is_file_in_repo_containment_and_prefix_collision():
    """Verify generic path containment and prefix collision prevention."""
    # Prefix collision tests
    assert is_file_in_repo("/repos/app2/main.py", "/repos/app") is False
    assert is_file_in_repo("C:\\repos\\app2\\main.py", "C:\\repos\\app") is False
    assert is_file_in_repo("/tmp/project_b/src/b.py", "/tmp/project_a") is False

    # Valid containment tests
    assert is_file_in_repo("/repos/app/src/main.py", "/repos/app") is True
    assert is_file_in_repo("C:\\repos\\app\\src\\main.py", "C:\\repos\\app") is True
    assert is_file_in_repo("src/main.py", "C:\\repos\\app") is True


def test_generic_multi_repo_isolation_tmp_dir(tmp_path):
    """Verify multi-repo isolation using temporary dummy repositories (repo_a and repo_b)."""
    repo_a = tmp_path / "repo_alpha"
    repo_b = tmp_path / "repo_beta"

    src_a = repo_a / "src"
    src_b = repo_b / "src"

    src_a.mkdir(parents=True)
    src_b.mkdir(parents=True)

    file_a = src_a / "alpha_module.py"
    file_b = src_b / "beta_module.py"

    file_a.write_text("def execute_alpha_pipeline():\n    return 'alpha_result'\n", encoding="utf-8")
    file_b.write_text("def execute_beta_pipeline():\n    return 'beta_result'\n", encoding="utf-8")

    # Index both dummy repos
    index_repository(repo_a)
    index_repository(repo_b)

    # Search targeting repo_a
    engine_a = RetrievalEngine(repo_path=str(repo_a))
    results_a = engine_a.search("execute pipeline", limit=10)

    for item in results_a:
        item_file = item.get("file", "")
        assert "repo_beta" not in item_file, f"Cross-repo leak! Found repo_beta item in repo_a search: {item_file}"
        if item_file:
            assert is_file_in_repo(item_file, str(repo_a)), f"Item file '{item_file}' not in repo_a!"

    # Search targeting repo_b
    engine_b = RetrievalEngine(repo_path=str(repo_b))
    results_b = engine_b.search("execute pipeline", limit=10)

    for item in results_b:
        item_file = item.get("file", "")
        assert "repo_alpha" not in item_file, f"Cross-repo leak! Found repo_alpha item in repo_b search: {item_file}"
        if item_file:
            assert is_file_in_repo(item_file, str(repo_b)), f"Item file '{item_file}' not in repo_b!"


def test_evidence_manager_generic_rejection(tmp_path):
    """Verify EvidenceManager generically rejects items outside active repo_path."""
    repo_a = tmp_path / "repo_alpha"
    repo_b = tmp_path / "repo_beta"
    repo_a.mkdir(parents=True)
    repo_b.mkdir(parents=True)

    mgr = EvidenceManager(repo_path=str(repo_a))

    # Add item belonging to repo_b -> should be rejected!
    mgr.add_item({
        "file": str(repo_b / "src" / "beta.py"),
        "content": "def beta(): pass",
        "start_line": 1,
        "end_line": 2
    })
    assert len(mgr.evidence_items) == 0, "EvidenceManager failed to reject cross-repo item from repo_b!"

    # Add item belonging to repo_a -> should be accepted!
    mgr.add_item({
        "file": str(repo_a / "src" / "alpha.py"),
        "content": "def alpha(): pass",
        "start_line": 1,
        "end_line": 2
    })
    assert len(mgr.evidence_items) == 1, "EvidenceManager failed to accept valid item from repo_a!"


def test_agent_dynamic_repo_scoping(tmp_path):
    """Verify agent investigation generically respects dynamically supplied repository paths."""
    repo_a = tmp_path / "repo_alpha"
    repo_b = tmp_path / "repo_beta"

    src_a = repo_a / "src"
    src_b = repo_b / "src"
    src_a.mkdir(parents=True)
    src_b.mkdir(parents=True)

    (src_a / "core_a.py").write_text("def process_data_a():\n    return 42\n", encoding="utf-8")
    (src_b / "core_b.py").write_text("def process_data_b():\n    return 99\n", encoding="utf-8")

    index_repository(repo_a)
    index_repository(repo_b)

    # Run agent on repo_a
    res_a = run_agent("How does process_data work?", repo_path=str(repo_a))
    evidence_a = res_a.get("evidence", [])
    for ev in evidence_a:
        ev_file = ev.get("file", "")
        assert "repo_beta" not in ev_file, f"Agent leaked repo_beta evidence when investigating repo_a: {ev_file}"

    # Run agent on repo_b
    res_b = run_agent("How does process_data work?", repo_path=str(repo_b))
    evidence_b = res_b.get("evidence", [])
    for ev in evidence_b:
        ev_file = ev.get("file", "")
        assert "repo_alpha" not in ev_file, f"Agent leaked repo_alpha evidence when investigating repo_b: {ev_file}"
