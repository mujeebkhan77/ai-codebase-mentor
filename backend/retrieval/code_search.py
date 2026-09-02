from pathlib import Path
from typing import Optional
from langchain_chroma import Chroma


def is_file_in_repo(file_path: str, repo_path: str) -> bool:
    """
    Safely determine if file_path is contained within target repo_path.
    Handles absolute paths, workspace-relative paths, repo-relative paths,
    Windows/Unix separators, and prevents prefix collisions (e.g. /repos/app vs /repos/app2).
    """
    if not file_path or not repo_path:
        return True

    raw_file_str = str(file_path).replace("\\", "/").strip()
    raw_repo_str = str(repo_path).replace("\\", "/").strip()

    repo_abs = Path(repo_path).resolve()
    file_p = Path(file_path)

    # 1. Absolute / Root-anchored path check
    if file_p.is_absolute() or raw_file_str.startswith("/") or (len(raw_file_str) > 1 and raw_file_str[1] == ":"):
        resolved_file = file_p.resolve()
        try:
            resolved_file.relative_to(repo_abs)
            return True
        except ValueError:
            pass

        repo_parts = [p.lower() for p in repo_abs.parts if p and p not in ("/", "\\")]
        file_parts = [p.lower() for p in resolved_file.parts if p and p not in ("/", "\\")]

        len_repo = len(repo_parts)
        len_file = len(file_parts)
        for i in range(len_file - len_repo + 1):
            if file_parts[i:i + len_repo] == repo_parts:
                return True
        return False

    # 2. Workspace-relative path check
    file_abs = file_p.resolve()
    try:
        file_abs.relative_to(repo_abs)
        return True
    except ValueError:
        pass

    file_parts = [p.lower() for p in file_abs.parts if p and p not in ("/", "\\")]
    repo_parts = [p.lower() for p in repo_abs.parts if p and p not in ("/", "\\")]
    len_repo = len(repo_parts)
    len_file = len(file_parts)

    for i in range(len_file - len_repo + 1):
        if file_parts[i:i + len_repo] == repo_parts:
            return True

    # 3. Relative child path check (e.g. 'src/main.py' or 'app.py')
    clean_rel = raw_file_str.lstrip("./")
    rel_parts = [p.lower() for p in Path(clean_rel).parts if p and p not in ("/", "\\")]
    repo_name = repo_abs.name.lower()

    if rel_parts and rel_parts[0] == "repositories" and len(rel_parts) > 1:
        if rel_parts[1] != repo_name:
            return False

    try:
        combined = (repo_abs / clean_rel).resolve()
        combined.relative_to(repo_abs)
        if "repositories" in [p.lower() for p in combined.parts]:
            comb_parts = [p.lower() for p in combined.parts]
            idx = comb_parts.index("repositories")
            if idx + 1 < len(comb_parts) and comb_parts[idx + 1] != repo_name:
                return False
        return True
    except ValueError:
        return False


def find_by_class(vectorstore: Chroma, class_name: str):

    results = vectorstore.get(
        where={
            "class": class_name
        }
    )

    documents = []

    for content, metadata in zip(
        results["documents"],
        results["metadatas"]
    ):
        documents.append({
            "content": content,
            "metadata": metadata
        })

    return documents


def find_by_function(vectorstore: Chroma, function_name: str):

    results = vectorstore.get(
        where={
            "name": function_name
        }
    )

    documents = []

    for content, metadata in zip(
        results["documents"],
        results["metadatas"]
    ):
        documents.append({
            "content": content,
            "metadata": metadata
        })

    return documents


def find_class_location(vectorstore: Chroma, class_name: str):

    results = vectorstore.get(
        where={
            "class": class_name
        }
    )

    locations = {}

    for metadata in results["metadatas"]:

        file_path = metadata.get("file")

        if not file_path:
            continue

        if file_path not in locations:
            locations[file_path] = {
                "file": file_path,
                "class": class_name,
                "start_line": metadata.get("start_line"),
                "end_line": metadata.get("end_line")
            }

    return list(locations.values())



def rerank_results(documents, query, top_k=5):

    query_lower = query.lower()

    scored_documents = []

    for document in documents:

        metadata = document["metadata"]

        score = 0

        file_path = metadata.get("file", "").replace("\\", "/")
        chunk_type = metadata.get("type")
        class_name = metadata.get("class")
        name = metadata.get("name")

        # Prefer actual source code
        if "/src/" in file_path:
            score += 5

        # Avoid tests
        if "/tests/" in file_path:
            score -= 5

        # Prefer actual class definitions
        if chunk_type == "class":
            score += 15

        # Prefer methods/functions when the query asks for them
        if "function" in query_lower or "method" in query_lower:
            if chunk_type in {"function", "method"}:
                score += 10

        # Prefer class-related results when query asks about a class
        if "class" in query_lower:
            if chunk_type == "class":
                score += 10

        # Match query words against metadata
        if class_name:
            if class_name.lower() in query_lower:
                score += 10

        if name:
            if name.lower() in query_lower:
                score += 10

        scored_documents.append(
            (score, document)
        )

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        document
        for score, document in scored_documents[:top_k]
    ]


def semantic_search(vectorstore, query, k=5, repo_path: Optional[str] = None):

    results = vectorstore.similarity_search(
        query,
        k=25
    )

    documents = []

    for doc in results:
        file_path = doc.metadata.get("file", "")
        if repo_path and not is_file_in_repo(file_path, repo_path):
            continue

        documents.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })

    return rerank_results(
        documents,
        query,
        top_k=k
    )