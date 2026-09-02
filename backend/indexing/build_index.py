from indexing.index_repository import index_repository
from embeddings import get_embeddings
from vectorstore import create_vectorstore

def build_index(repo_path):

    documents = index_repository(repo_path)

    embeddings = get_embeddings()

    vectorstore = create_vectorstore(
        documents,
        embeddings
    )

    return vectorstore