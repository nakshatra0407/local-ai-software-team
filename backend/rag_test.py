from retriever import Retriever
from context_builder import build_context
from qwen_client import ask_qwen


def build_rag_prompt(query, context):
    """
    Build a prompt that gives Qwen
    both the user's question and
    the retrieved knowledge.
    """

    prompt = f"""
You are an AI assistant.

Answer the user's question using the
relevant knowledge provided below.

RELEVANT KNOWLEDGE:

{context}

USER QUESTION:

{query}

Instructions:

1. Use the relevant knowledge when answering.
2. Do not invent information that conflicts with the knowledge.
3. Give a clear and concise answer.
4. If the knowledge does not contain enough information,
   say that the provided knowledge is insufficient.

ANSWER:
"""

    return prompt


if __name__ == "__main__":

    query = (
        "How should I protect an AI agent "
        "from unsafe file access?"
    )

    print("Creating Retriever...")
    retriever = Retriever(top_k=3)

    print("\nRetrieving relevant knowledge...")

    results = retriever.retrieve(query)

    print("\nBuilding context...")

    context = build_context(results)

    prompt = build_rag_prompt(
        query,
        context
    )

    print("\nSending context to Qwen...")

    answer = ask_qwen(prompt)

    print("\n===== RAG ANSWER =====")
    print(answer)
    print("===== END RAG ANSWER =====")