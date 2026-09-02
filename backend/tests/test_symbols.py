import json
from indexing.symbols import extract_symbols
from retrieval.symbol_search import find_symbol


def test_extract_symbols(temp_repo):
    proc_file = temp_repo / "src" / "processor.py"
    symbols = extract_symbols(proc_file)

    assert len(symbols) == 5  # Class Processor, __init__, run, validate, execute

    sym_names = [s["name"] for s in symbols]
    assert "Processor" in sym_names
    assert "run" in sym_names
    assert "validate" in sym_names

    class_sym = next(s for s in symbols if s["name"] == "Processor")
    assert class_sym["type"] == "class"

    method_sym = next(s for s in symbols if s["name"] == "run")
    assert method_sym["type"] == "method"
    assert method_sym["class"] == "Processor"


def test_find_symbol(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sample_symbols = [
        {"name": "Flask", "type": "class", "class": None, "file": "src/flask/app.py", "start_line": 10, "end_line": 100},
        {"name": "wsgi_app", "type": "method", "class": "Flask", "file": "src/flask/app.py", "start_line": 50, "end_line": 80}
    ]
    with open(tmp_path / "symbol_index.json", "w", encoding="utf-8") as f:
        json.dump(sample_symbols, f)

    results = find_symbol("Flask")
    assert len(results) == 1
    assert results[0]["name"] == "Flask"
    assert results[0]["type"] == "class"

    results_lower = find_symbol("wsgi_app")
    assert len(results_lower) == 1
    assert results_lower[0]["class"] == "Flask"
