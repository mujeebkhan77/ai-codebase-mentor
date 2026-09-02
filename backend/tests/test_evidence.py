from evidence.manager import EvidenceManager


def test_evidence_manager_deduplication():
    em = EvidenceManager()
    item1 = {"file": "src/app.py", "start_line": 10, "end_line": 20, "symbol": "run", "content": "def run(): pass", "rank_score": 0.8}
    item2 = {"file": "src/app.py", "start_line": 10, "end_line": 20, "symbol": "run", "content": "def run(): pass", "rank_score": 0.8}

    em.add_item(item1)
    em.add_item(item2)

    assert len(em.evidence_items) == 2
    em.deduplicate()
    assert len(em.evidence_items) == 1


def test_evidence_manager_overlapping_ranges_merging():
    em = EvidenceManager()
    # Overlapping line ranges from same file
    item1 = {"file": "src/app.py", "start_line": 10, "end_line": 25, "symbol": "run", "content": "def run():\n    pass", "rank_score": 0.8}
    item2 = {"file": "src/app.py", "start_line": 20, "end_line": 35, "symbol": "run_helper", "content": "    run_helper()", "rank_score": 0.9}

    em.add_items([item1, item2])
    em.merge_overlapping_ranges()

    assert len(em.evidence_items) == 1
    merged = em.evidence_items[0]
    assert merged["start_line"] == 10
    assert merged["end_line"] == 35
    assert merged["rank_score"] == 0.9
    assert "run" in merged["symbol"]
    assert "run_helper" in merged["symbol"]


def test_evidence_manager_formatting_and_budgeting():
    em = EvidenceManager()
    for i in range(10):
        em.add_item({
            "file": f"src/module_{i}.py",
            "start_line": 1,
            "end_line": 50,
            "symbol": f"func_{i}",
            "content": f"def func_{i}():\n    return {i}",
            "rank_score": 0.5 + (i * 0.05)
        })

    # Prioritizes higher rank score (func_9, func_8...)
    prioritized = em.get_prioritized_evidence(max_items=3)
    assert len(prioritized) == 3
    assert prioritized[0]["symbol"] == "func_9"

    formatted = em.format_for_llm(max_items=3)
    assert "### Evidence 1: src/module_9.py" in formatted
    assert "def func_9():" in formatted
