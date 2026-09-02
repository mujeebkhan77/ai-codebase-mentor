import os
import shutil
import tempfile
import pytest
from pathlib import Path


@pytest.fixture
def temp_repo(tmp_path):
    """
    Creates a temporary synthetic Python repository structure for testing.
    """
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir()

    src_dir = repo_dir / "src"
    src_dir.mkdir()

    tests_dir = repo_dir / "tests"
    tests_dir.mkdir()

    # Create config file
    pyproject = repo_dir / "pyproject.toml"
    pyproject.write_text("[project]\nname = 'test_repo'\nversion = '0.1.0'\n", encoding="utf-8")

    # Create main.py
    main_file = repo_dir / "main.py"
    main_file.write_text(
        "def entry_point():\n"
        "    app = Processor()\n"
        "    app.run()\n\n"
        "if __name__ == '__main__':\n"
        "    entry_point()\n",
        encoding="utf-8"
    )

    # Create src/processor.py
    proc_file = src_dir / "processor.py"
    proc_file.write_text(
        "class Processor:\n"
        "    def __init__(self):\n"
        "        self.status = 'ready'\n\n"
        "    def run(self):\n"
        "        self.validate()\n"
        "        self.execute()\n\n"
        "    def validate(self):\n"
        "        return True\n\n"
        "    def execute(self):\n"
        "        print('Executing processor')\n",
        encoding="utf-8"
    )

    # Create tests/test_processor.py
    test_file = tests_dir / "test_processor.py"
    test_file.write_text(
        "def test_run():\n"
        "    p = Processor()\n"
        "    p.run()\n",
        encoding="utf-8"
    )

    return repo_dir
