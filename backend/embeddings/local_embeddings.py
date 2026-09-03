from sentence_transformers import SentenceTransformer


class LocalEmbeddings:

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def embed_documents(self, texts):
        return self.model.encode(
            texts,
            batch_size=8,
            show_progress_bar=True
        ).tolist()

    def embed_query(self, text):
        return self.model.encode(
            [text]
        )[0].tolist()


def get_embeddings():
    return LocalEmbeddings()