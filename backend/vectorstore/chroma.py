from langchain_chroma import Chroma


def create_vectorstore(documents, embeddings):

    texts = []
    metadatas = []

    for doc in documents:
        texts.append(doc.page_content)
        metadatas.append(doc.metadata)

    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="chroma_db"
    )

    batch_size = 128

    for i in range(0, len(texts), batch_size):

        batch_texts = texts[i:i + batch_size]
        batch_metadata = metadatas[i:i + batch_size]

        print(
            f"Embedding batch {i} - "
            f"{i + len(batch_texts)}"
        )

        vectorstore.add_texts(
            texts=batch_texts,
            metadatas=batch_metadata
        )

    return vectorstore

def get_vectorstore(embeddings):
    """
    Load the existing persisted ChromaDB vector store.
    """

    vectorstore = Chroma(
        embedding_function=embeddings,
        persist_directory="chroma_db"
    )

    return vectorstore