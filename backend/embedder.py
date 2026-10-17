from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:

    def __init__(self):
        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

    def embed_text(self, text):

        vector = self.model.encode(
            text
        )

        return vector

    def embed_texts(self, texts):

        vectors = self.model.encode(
            texts
        )

        return vectors


if __name__ == "__main__":

    embedder = Embedder()

    text = "Use pytest for Python testing."

    vector = embedder.embed_text(
        text
    )

    print(
        "\nText:"
    )

    print(text)

    print(
        "\nEmbedding type:"
    )

    print(type(vector))

    print(
        "\nEmbedding dimensions:"
    )

    print(vector.shape)

    print(
        "\nFirst 10 values:"
    )

    print(vector[:10])