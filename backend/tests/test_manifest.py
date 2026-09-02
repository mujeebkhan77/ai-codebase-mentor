from indexing.manifest import generate_manifest


def test_generate_manifest(temp_repo):
    symbols = [
        {"name": "Processor", "type": "class"},
        {"name": "run", "type": "method"},
    ]
    rels = [
        {"caller": "run", "callee": "validate"}
    ]

    manifest = generate_manifest(temp_repo, symbols=symbols, relationships=rels)

    assert manifest["repository_name"] == "test_repo"
    assert manifest["total_files"] >= 4
    assert manifest["languages"].get("python") >= 3
    assert "pyproject.toml" in manifest["config_files"]
    assert "main.py" in manifest["entry_points"]
    assert manifest["symbols_summary"]["total_symbols"] == 2
    assert manifest["relationships_summary"]["total_relationships"] == 1
