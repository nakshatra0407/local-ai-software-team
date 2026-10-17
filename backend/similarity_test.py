from embedder import Embedder

import numpy as np


def cosine_similarity(vector_a, vector_b):
    """
    Calculate cosine similarity between two vectors.
    """

    dot_product = np.dot(
        vector_a,
        vector_b
    )

    magnitude_a = np.linalg.norm(
        vector_a
    )

    magnitude_b = np.linalg.norm(
        vector_b
    )

    return dot_product / (
        magnitude_a * magnitude_b
    )


if __name__ == "__main__":

    embedder = Embedder()

    query = (
        "How should I write tests for a Python project?"
    )

    texts = [
        "Use pytest for Python testing.",
        "FastAPI routes should use HTTP methods.",
        "Never hardcode API keys."
    ]

    query_vector = embedder.embed_text(
        query
    )

    text_vectors = embedder.embed_texts(
        texts
    )

    print("\nQUERY:")
    print(query)

    print("\nSIMILARITY RESULTS:")

    for text, vector in zip(
        texts,
        text_vectors
    ):

        similarity = cosine_similarity(
            query_vector,
            vector
        )

        print(
            f"{similarity:.4f} - {text}"
        )