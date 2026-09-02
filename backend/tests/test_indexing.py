import json
from indexing.index_repository import index_repository


def test_index_repository(temp_repo, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    chunks = index_repository(temp_repo)

    assert len(chunks) > 0

    # Verify generated index files
    symbol_file = tmp_path / "symbol_index.json"
    rel_file = tmp_path / "relationship_index.json"
    manifest_file = tmp_path / "repository_manifest.json"

    assert symbol_file.exists()
    assert rel_file.exists()
    assert manifest_file.exists()

    with open(symbol_file, "r", encoding="utf-8") as f:
        symbols = json.load(f)
    assert len(symbols) > 0
    names = [s["name"] for s in symbols]
    assert "Processor" in names
    assert "run" in names

    with open(rel_file, "r", encoding="utf-8") as f:
        rels = json.load(f)
    assert isinstance(rels, list)

    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["repository_name"] == "test_repo"
    assert "python" in manifest["languages"]
