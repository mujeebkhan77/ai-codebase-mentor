import json
from indexing.relationships import extract_relationships, resolve_relationships
from retrieval.relationship_search import find_relationships


def test_extract_and_resolve_relationships(temp_repo):
    proc_file = temp_repo / "src" / "processor.py"
    raw_rels = extract_relationships(proc_file)

    # Processor.run() calls self.validate() and self.execute()
    callees = [r["callee"] for r in raw_rels]
    assert "self.validate" in callees
    assert "self.execute" in callees

    sample_symbols = [
        {"name": "Processor", "type": "class", "class": None, "file": str(proc_file), "start_line": 1, "end_line": 15},
        {"name": "run", "type": "method", "class": "Processor", "file": str(proc_file), "start_line": 5, "end_line": 8},
        {"name": "validate", "type": "method", "class": "Processor", "file": str(proc_file), "start_line": 9, "end_line": 11},
        {"name": "execute", "type": "method", "class": "Processor", "file": str(proc_file), "start_line": 12, "end_line": 14},
    ]

    resolved = resolve_relationships(raw_rels, sample_symbols)
    assert len(resolved) == 2

    resolved_callees = [r["callee"] for r in resolved]
    assert "validate" in resolved_callees
    assert "execute" in resolved_callees


def test_find_relationships(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sample_rels = [
        {
            "caller": "run",
            "callee": "validate",
            "file": "src/processor.py",
            "line": 6,
            "target_file": "src/processor.py",
            "target_class": "Processor",
            "target_type": "method"
        }
    ]

    with open(tmp_path / "relationship_index.json", "w", encoding="utf-8") as f:
        json.dump(sample_rels, f)

    res_outgoing = find_relationships("run", direction="outgoing")
    assert len(res_outgoing["outgoing"]) == 1
    assert res_outgoing["outgoing"][0]["callee"] == "validate"

    res_incoming = find_relationships("validate", direction="incoming")
    assert len(res_incoming["incoming"]) == 1
    assert res_incoming["incoming"][0]["caller"] == "run"
