import ast
from pathlib import Path

from langchain_core.documents import Document


def chunk_python_file(file_path):

    chunks = []

    source_code = Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return chunks

    lines = source_code.splitlines()

    for node in ast.iter_child_nodes(tree):

        # Standalone functions
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            chunks.append(
                create_chunk(
                    node,
                    lines,
                    file_path,
                    "function",
                    None
                )
            )

        # Classes
        elif isinstance(node, ast.ClassDef):

            class_name = node.name

            # Extract methods inside class
            for item in node.body:

                if isinstance(
                    item,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):

                    chunks.append(
                        create_chunk(
                            item,
                            lines,
                            file_path,
                            "method",
                            class_name
                        )
                    )

    return chunks


def create_chunk(node, lines, file_path, chunk_type, class_name):

    start = node.lineno
    end = node.end_lineno

    code = "\n".join(
        lines[start - 1:end]
    )

    return Document(
        page_content=code,
        metadata={
            "file": str(file_path),
            "type": chunk_type,
            "class": class_name,
            "name": node.name,
            "start_line": start,
            "end_line": end,
        },
    )