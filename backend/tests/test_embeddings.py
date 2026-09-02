from embeddings.local_embeddings import LocalEmbeddings


def test_local_embeddings():
    embeddings = LocalEmbeddings()
    texts = ["def foo(): return 42", "class Bar: pass"]

    # Test document embeddings
    doc_vectors = embeddings.embed_documents(texts)
    assert len(doc_vectors) == 2
    assert isinstance(doc_vectors[0], list)
    assert len(doc_vectors[0]) == 384  # BAAI/bge-small-en-v1.5 output dimension

    # Test query embedding
    query_vector = embeddings.embed_query("search term")
    assert isinstance(query_vector, list)
    assert len(query_vector) == 384
