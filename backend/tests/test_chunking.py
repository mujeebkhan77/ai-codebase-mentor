from indexing.chunking import chunk_python_file


def test_chunk_python_file(temp_repo):
    proc_file = temp_repo / "src" / "processor.py"
    chunks = chunk_python_file(proc_file)

    assert len(chunks) == 4  # __init__, run, validate, execute methods

    # Verify chunk metadata
    methods = [c.metadata["name"] for c in chunks]
    assert "run" in methods
    assert "validate" in methods
    assert "execute" in methods

    for chunk in chunks:
        assert chunk.metadata["class"] == "Processor"
        assert chunk.metadata["type"] == "method"
        assert chunk.metadata["start_line"] > 0
        assert chunk.metadata["end_line"] >= chunk.metadata["start_line"]
