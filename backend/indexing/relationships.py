import ast
import json
from pathlib import Path


def extract_relationships(file_path):
    """
    Extract function/method call relationships from a Python file.

    Each relationship contains:
    - caller
    - callee
    - file
    - line
    """

    relationships = []

    source_code = Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    )

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return relationships

    for node in ast.walk(tree):

        if not isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue

        caller = node.name

        for child in ast.walk(node):

            if not isinstance(child, ast.Call):
                continue

            callee = get_called_name(child)

            if not callee:
                continue

            relationships.append(
                {
                    "file": str(file_path),
                    "caller": caller,
                    "callee": callee,
                    "line": child.lineno
                }
            )

    return relationships


def get_called_name(call_node):
    """
    Convert an AST Call node into a readable name.

    foo()
        -> foo

    obj.foo()
        -> obj.foo

    self.foo()
        -> self.foo
    """

    function = call_node.func

    if isinstance(function, ast.Name):
        return function.id

    if isinstance(function, ast.Attribute):

        parts = []

        current = function

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(reversed(parts))

    return None


def load_symbol_index():
    """
    Load the existing symbol index created during repository indexing.
    """

    symbol_index_path = Path("symbol_index.json")

    if not symbol_index_path.exists():
        return []

    with open(
        symbol_index_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def resolve_relationships(relationships, symbols):
    """
    Resolve function/method calls against the existing symbol index.

    Resolution strategy:
    1. Ignore Python built-ins.
    2. Resolve self.method() using the caller's class.
    3. Resolve ClassName.method() using the explicit class.
    4. Prefer symbols from the same file.
    5. For plain function calls, only resolve when the target is
       unambiguous.
    6. Never guess when multiple unrelated targets exist.
    """

    resolved = []

    # ---------------------------------------------------------
    # Python built-ins that should NOT become repository
    # relationships.
    # ---------------------------------------------------------

    BUILTINS = {
        "abs",
        "all",
        "any",
        "ascii",
        "bin",
        "bool",
        "breakpoint",
        "bytearray",
        "bytes",
        "callable",
        "chr",
        "classmethod",
        "compile",
        "complex",
        "delattr",
        "dict",
        "dir",
        "divmod",
        "enumerate",
        "eval",
        "exec",
        "filter",
        "float",
        "format",
        "frozenset",
        "getattr",
        "globals",
        "hasattr",
        "hash",
        "help",
        "hex",
        "id",
        "input",
        "int",
        "isinstance",
        "issubclass",
        "iter",
        "len",
        "list",
        "locals",
        "map",
        "max",
        "memoryview",
        "min",
        "next",
        "object",
        "oct",
        "open",
        "ord",
        "pow",
        "print",
        "property",
        "range",
        "repr",
        "reversed",
        "round",
        "set",
        "setattr",
        "slice",
        "sorted",
        "staticmethod",
        "str",
        "sum",
        "super",
        "tuple",
        "type",
        "vars",
        "zip",
        "__import__",
    }

    # ---------------------------------------------------------
    # Build quick lookup indexes from symbol_index.json
    # ---------------------------------------------------------

    symbols_by_name = {}
    symbols_by_file = {}

    for symbol in symbols:

        name = symbol.get("name")
        file_path = symbol.get("file")

        if not name:
            continue

        # Normalize path separators
        if file_path:
            file_path = str(file_path).replace("\\", "/")
            symbol["file"] = file_path

        symbols_by_name.setdefault(
            name,
            []
        ).append(symbol)

        if file_path:
            symbols_by_file.setdefault(
                file_path,
                []
            ).append(symbol)

    # ---------------------------------------------------------
    # Find the class containing the caller
    # ---------------------------------------------------------

    def find_caller_class(caller_file, caller_name, caller_line):

        file_symbols = symbols_by_file.get(
            caller_file,
            []
        )

        candidates = []

        for symbol in file_symbols:

            if symbol.get("name") != caller_name:
                continue

            if symbol.get("type") != "method":
                continue

            start = symbol.get("start_line")
            end = symbol.get("end_line")

            if start is None or end is None:
                continue

            # The caller's definition should contain the
            # relationship's call line.
            if start <= caller_line <= end:
                candidates.append(symbol)

        # Prefer the smallest containing method.
        if candidates:
            candidates.sort(
                key=lambda symbol:
                (
                    symbol.get("end_line", 10**9)
                    - symbol.get("start_line", 0)
                )
            )

            return candidates[0].get("class")

        return None

    # ---------------------------------------------------------
    # Process every raw relationship
    # ---------------------------------------------------------

    for relationship in relationships:

        callee = relationship.get("callee")

        if not callee:
            continue

        caller_file = str(
            relationship.get("file", "")
        ).replace("\\", "/")

        caller_name = relationship.get(
            "caller"
        )

        call_line = relationship.get(
            "line"
        )

        # -----------------------------------------------------
        # Extract actual callable name
        #
        # Examples:
        #
        # foo()                  -> foo
        # self.foo()             -> foo
        # app.foo()              -> foo
        # Flask.foo()            -> foo
        # obj.foo.bar()          -> bar
        # -----------------------------------------------------

        parts = callee.split(".")

        lookup_name = parts[-1]

        # -----------------------------------------------------
        # Ignore Python built-ins
        # -----------------------------------------------------

        if lookup_name in BUILTINS:
            continue

        # -----------------------------------------------------
        # Find all repository symbols with this name
        # -----------------------------------------------------

        matches = symbols_by_name.get(
            lookup_name,
            []
        )

        if not matches:
            continue

        selected = []

        # -----------------------------------------------------
        # CASE 1:
        # self.foo()
        #
        # Resolve foo inside the caller's class.
        # -----------------------------------------------------

        caller_class = None

        if (
            parts[0] == "self"
            and call_line is not None
        ):
            caller_class = find_caller_class(
                caller_file,
                caller_name,
                call_line
            )

        if caller_class:

            selected = [
                symbol
                for symbol in matches
                if (
                    symbol.get("class") == caller_class
                    and symbol.get("file") == caller_file
                )
            ]

        # -----------------------------------------------------
        # CASE 2:
        # ClassName.foo()
        #
        # Example:
        #
        # Flask.ensure_sync()
        #
        # Resolve foo inside Flask.
        # -----------------------------------------------------

        if not selected and len(parts) >= 2:

            object_name = parts[-2]

            class_matches = [
                symbol
                for symbol in matches
                if symbol.get("class") == object_name
            ]

            if len(class_matches) == 1:
                selected = class_matches

            elif len(class_matches) > 1:

                # Prefer the same file if possible.
                same_file = [
                    symbol
                    for symbol in class_matches
                    if symbol.get("file") == caller_file
                ]

                if len(same_file) == 1:
                    selected = same_file

        # -----------------------------------------------------
        # CASE 3:
        # Plain function call
        #
        # Example:
        #
        # load_config()
        #
        # First prefer a function in the same file.
        # -----------------------------------------------------

        if not selected and len(parts) == 1:

            same_file_matches = [
                symbol
                for symbol in matches
                if symbol.get("file") == caller_file
            ]

            # Only accept if there is exactly one.
            if len(same_file_matches) == 1:
                selected = same_file_matches

        # -----------------------------------------------------
        # CASE 4:
        # Unique repository-wide symbol
        #
        # If only ONE symbol with this name exists anywhere,
        # it is safe to resolve.
        # -----------------------------------------------------

        if not selected:

            unique_matches = [
                symbol
                for symbol in matches
                if symbol.get("type")
                in {"function", "class"}
            ]

            if len(unique_matches) == 1:
                selected = unique_matches

        # -----------------------------------------------------
        # If we still don't know the target, DON'T GUESS.
        # -----------------------------------------------------

        if not selected:
            continue

        # -----------------------------------------------------
        # Create resolved relationship
        # -----------------------------------------------------

        for match in selected:

            resolved.append(
                {
                    "file": caller_file,

                    "caller": caller_name,

                    "callee": lookup_name,

                    "line": call_line,

                    "target_file": str(
                        match.get("file", "")
                    ).replace("\\", "/"),

                    "target_class": match.get(
                        "class"
                    ),

                    "target_type": match.get(
                        "type"
                    ),

                    "target_start_line": match.get(
                        "start_line"
                    ),

                    "target_end_line": match.get(
                        "end_line"
                    )
                }
            )

    return resolved