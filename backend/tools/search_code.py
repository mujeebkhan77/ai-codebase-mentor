import os

def search_code(query: str, repo_path: str):
    """
    Search the repository source code to locate relevant files.

    Use this tool when you need to find:
    - classes
    - functions
    - variables
    - implementations
    - where a feature exists in the codebase

    Examples:
    - Find where Flask class is implemented
    - Find authentication logic
    - Find database connection code

    Input:
    query: class name, function name, keyword, or concept to search for.

    Output:
    Returns file paths containing the searched term.
    
    Search keyword inside repository files
    and return relevant code snippets with line numbers.
    """

    results = []

    ignore_dirs = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv"
    }

    extensions = {
        ".py",
        ".js",
        ".ts",
        ".java",
        ".cpp",
        ".c",
        ".go"
    }


    for root, dirs, files in os.walk(repo_path):

        # remove ignored folders
        dirs[:] = [
            d for d in dirs 
            if d not in ignore_dirs
        ]


        for file in files:

            ext = os.path.splitext(file)[1]

            if ext not in extensions:
                continue


            file_path = os.path.join(
                root,
                file
            )


            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    lines = f.readlines()


                for index, line in enumerate(lines):

                    if query.lower() in line.lower():

                        start = max(
                            0,
                            index - 3
                        )

                        end = min(
                            len(lines),
                            index + 4
                        )


                        snippet = "".join(
                            lines[start:end]
                        )


                        results.append(
                            {
                                "file": file_path,
                                "line": index + 1,
                                "start_line": start + 1,
                                "end_line": end,
                                "snippet": snippet
                            }
                        )


            except Exception:
                continue


    return results[:10]