from pathlib import Path


def read_file(
    file_path: str,
    start_line: int | None = None,
    end_line: int | None = None
):
    """
    Read a source code file.

    If start_line and end_line are provided, only that line range is returned.
    Otherwise, the complete file is returned.
    """
    path = Path(file_path)
    if not path.exists():
        return f"Error: File '{file_path}' does not exist."

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"

    total_lines = len(lines)
    if total_lines == 0:
        return f"File '{file_path}' is empty."

    if start_line is not None or end_line is not None:
        start = max(1, start_line or 1)
        end = min(total_lines, end_line if end_line is not None else total_lines)

        if start > total_lines:
            return f"Error: start_line {start} exceeds total lines ({total_lines}) in file '{file_path}'."

        if start > end:
            return f"Error: start_line ({start}) cannot be greater than end_line ({end})."

        selected_lines = lines[start - 1:end]
        return "".join(
            f"{i + start}: {line}"
            for i, line in enumerate(selected_lines)
        )

    return "".join(
        f"{i + 1}: {line}"
        for i, line in enumerate(lines)
    )