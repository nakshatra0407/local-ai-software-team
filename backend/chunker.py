from document_loader import load_documents


def chunk_document(content):
    """
    Split a document into chunks using blank lines.
    """

    raw_chunks = content.split("\n\n")

    chunks = []

    for chunk in raw_chunks:

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def create_chunks():

    documents = load_documents()

    all_chunks = []

    for document in documents:

        chunks = chunk_document(
            document["content"]
        )

        for chunk in chunks:

            all_chunks.append(
                {
                    "filename": document["filename"],
                    "content": chunk
                }
            )

    return all_chunks


if __name__ == "__main__":

    chunks = create_chunks()

    print(
        f"Created {len(chunks)} chunks."
    )

    for index, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"\n--- Chunk {index} "
            f"({chunk['filename']}) ---"
        )

        print(
            chunk["content"]
        )