from vector_store import VectorStore


class Retriever:

    def __init__(self, top_k=3):
        """
        Create a retriever with a vector store.

        top_k determines how many relevant
        chunks should be returned.
        """
        self.top_k = top_k
        self.vector_store = VectorStore()

        # Build the FAISS index when the retriever starts.
        self.vector_store.build()

    def retrieve(self, query):
        """
        Retrieve the most relevant knowledge chunks
        for the given query.
        """

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        results = self.vector_store.search(
            query,
            k=self.top_k
        )

        return results


if __name__ == "__main__":

    retriever = Retriever(top_k=3)

    query = (
        "How should I protect an AI agent "
        "from unsafe file access?"
    )

    results = retriever.retrieve(query)

    print("\nQUERY:")
    print(query)

    print("\nRETRIEVED KNOWLEDGE:")

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