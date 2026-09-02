import json
from graph.code_graph import CodeGraph


def test_code_graph_operations(tmp_path):
    sym_file = tmp_path / "symbol_index.json"
    rel_file = tmp_path / "relationship_index.json"

    symbols = [
        {"name": "Processor", "type": "class", "class": None, "file": "src/processor.py", "start_line": 1, "end_line": 20},
        {"name": "run", "type": "method", "class": "Processor", "file": "src/processor.py", "start_line": 5, "end_line": 10},
        {"name": "validate", "type": "method", "class": "Processor", "file": "src/processor.py", "start_line": 11, "end_line": 15},
    ]

    relationships = [
        {"caller": "run", "callee": "validate", "file": "src/processor.py", "line": 7, "target_file": "src/processor.py"},
        {"caller": "main", "callee": "run", "file": "main.py", "line": 3, "target_file": "src/processor.py"}
    ]

    with open(sym_file, "w", encoding="utf-8") as f:
        json.dump(symbols, f)
    with open(rel_file, "w", encoding="utf-8") as f:
        json.dump(relationships, f)

    graph = CodeGraph(symbol_index_path=sym_file, relationship_index_path=rel_file)

    # Outgoing calls
    out_calls = graph.get_outgoing_calls("run")
    assert len(out_calls) == 1
    assert out_calls[0]["callee"] == "validate"

    # Incoming callers
    in_callers = graph.get_incoming_callers("run")
    assert len(in_callers) == 1
    assert in_callers[0]["caller"] == "main"

    # Class methods
    methods = graph.get_class_methods("Processor")
    assert len(methods) == 2

    # File symbols
    proc_syms = graph.get_file_symbols("src/processor.py")
    assert len(proc_syms) == 3

    # Symbol file lookup
    run_file = graph.get_symbol_file("run")
    assert len(run_file) == 1
    assert run_file[0]["file"] == "src/processor.py"

    # Multi-hop call chain
    chain = graph.get_call_chain("main", max_depth=2, direction="outgoing")
    assert len(chain) == 2
    assert chain[0]["from"] == "main"
    assert chain[0]["to"] == "run"
    assert chain[1]["from"] == "run"
    assert chain[1]["to"] == "validate"
