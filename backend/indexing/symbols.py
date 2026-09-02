import ast
from pathlib import Path


def extract_symbols(file_path):

    file_path = Path(file_path)

    source_code = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []

    symbols = []

    for node in ast.iter_child_nodes(tree):

        # Top-level functions
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            symbols.append({
                "name": node.name,
                "type": "function",
                "class": None,
                "file": str(file_path),
                "start_line": node.lineno,
                "end_line": node.end_lineno,
            })

        # Classes
        elif isinstance(node, ast.ClassDef):

            class_name = node.name

            # Class itself
            symbols.append({
                "name": class_name,
                "type": "class",
                "class": None,
                "file": str(file_path),
                "start_line": node.lineno,
                "end_line": node.end_lineno,
            })

            # Methods inside class
            for item in node.body:

                if isinstance(
                    item,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):

                    symbols.append({
                        "name": item.name,
                        "type": "method",
                        "class": class_name,
                        "file": str(file_path),
                        "start_line": item.lineno,
                        "end_line": item.end_lineno,
                    })

    return symbols