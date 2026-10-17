import faiss
import numpy as np

from chunker import create_chunks
from embedder import Embedder


class VectorStore:

    def __init__(self):
        self.embedder = Embedder()
        self.chunks = create_chunks()
        self.vectors = None
        self.index = None

    def build(self):
        """
        Create embeddings for all chunks
        and store them in a FAISS index.
        """

        texts = [
            chunk["content"]
            for chunk in self.chunks
        ]

        print(
            f"Embedding {len(texts)} chunks..."
        )

        self.vectors = self.embedder.embed_texts(
            texts
        )

        self.vectors = np.asarray(
            self.vectors,
            dtype="float32"
        )

        dimension = self.vectors.shape[1]

        print(
            f"Vector dimension: {dimension}"
        )

        # Create FAISS index using inner product.
        # After normalization, inner product behaves
        # like cosine similarity.
        self.index = faiss.IndexFlatIP(
            dimension
        )

        # Normalize document vectors.
        faiss.normalize_L2(
            self.vectors
        )

        # Add vectors to FAISS.
        self.index.add(
            self.vectors
        )

        print(
            f"FAISS index contains "
            f"{self.index.ntotal} vectors."
        )

    def search(self, query, k=3):
        """
        Search the FAISS index for the most
        relevant chunks for a query.
        """

        if self.index is None:
            raise RuntimeError(
                "FAISS index has not been built."
            )

        # Convert the user's query into an embedding.
        query_vector = self.embedder.embed_text(
            query
        )

        # FAISS expects a 2D float32 NumPy array.
        query_vector = np.asarray(
            [query_vector],
            dtype="float32"
        )

        # Normalize the query vector so that
        # similarity behaves like cosine similarity.
        faiss.normalize_L2(
            query_vector
        )

        # Search for the top-k most similar vectors.
        scores, indices = self.index.search(
            query_vector,
            k
        )

        results = []

        # Match FAISS results back to our original chunks.
        for score, index in zip(
            scores[0],
            indices[0]
        ):
            chunk = self.chunks[index]

            results.append(
                {
                    "score": float(score),
                    "filename": chunk["filename"],
                    "content": chunk["content"]
                }
            )

        return results


if __name__ == "__main__":

    # Create the vector store.
    store = VectorStore()

    # Build the FAISS index.
    store.build()

    # Test query.
    query = (
        "How can I prevent an AI agent "
        "from accessing arbitrary files?"
    )

    # Search for the top 3 relevant chunks.
    results = store.search(
        query,
        k=3
    )

    print("\nQUERY:")
    print(query)

    print("\nRETRIEVED RESULTS:")

    for index, result in enumerate(
        results,
        start=1
    ):
        print(
            f"\n--- Result {index} ---"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Source: {result['filename']}"
        )

        print(
            f"Content: {result['content']}"
        )