from retriever import Retriever


def build_context(results):
    """
    Convert retrieved knowledge chunks into
    a single text context for the LLM.
    """

    if not results:
        return "No relevant knowledge was found."

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):
        context_parts.append(
            f"""
[Knowledge {index}]
Source: {result["filename"]}
Similarity Score: {result["score"]:.4f}

{result["content"]}
""".strip()
        )

    context = "\n\n".join(context_parts)

    return context


if __name__ == "__main__":

    retriever = Retriever(top_k=3)

    query = (
        "How should I protect an AI agent "
        "from unsafe file access?"
    )

    results = retriever.retrieve(query)

    context = build_context(results)

    print("\nQUERY:")
    print(query)

    print("\n===== GENERATED CONTEXT =====")
    print(context)
    print("===== END CONTEXT =====")