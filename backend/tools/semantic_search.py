from vectorstore.chroma import get_vectorstore
from embeddings.local_embeddings import LocalEmbeddings
from retrieval.code_search import semantic_search as run_semantic_search


def semantic_code_search(
    query: str,
    repo_path: str = None,
    k: int = 5
):
    """
    Search the repository using semantic/vector search.
    """

    embeddings = LocalEmbeddings()

    vectorstore = get_vectorstore(
        embeddings
    )

    results = run_semantic_search(
        vectorstore,
        query,
        k=k,
        repo_path=repo_path
    )

    return results