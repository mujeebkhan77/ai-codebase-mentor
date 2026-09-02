from sentence_transformers import SentenceTransformer


def get_embeddings():
    return SentenceTransformer(
        "BAAI/bge-small-en-v1.5"
    )