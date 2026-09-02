from tools.read_file import read_file
from tools.get_repository_structure import get_repository_structure


def test_read_file_tool(temp_repo):
    proc_file = str(temp_repo / "src" / "processor.py")

    # Read entire file
    full_content = read_file(proc_file)
    assert "class Processor:" in full_content
    assert "1: class Processor:" in full_content

    # Read specific line range
    range_content = read_file(proc_file, start_line=1, end_line=3)
    assert "1: class Processor:" in range_content
    assert "3: " in range_content
    assert "4: " not in range_content

    # Non-existent file error handling
    missing_res = read_file("nonexistent/file.py")
    assert "Error:" in missing_res


def test_get_repository_structure_tool(temp_repo):
    struct = get_repository_structure(str(temp_repo))
    assert "src/" in struct
    assert "tests/" in struct
    assert "pyproject.toml" in struct

    # Missing directory error handling
    missing_struct = get_repository_structure("nonexistent_path_xyz")
    assert "Error:" in missing_struct
