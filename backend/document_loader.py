from pathlib import Path


# Project root:
# D:\local-ai-software-team
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Knowledge directory:
# D:\local-ai-software-team\knowledge
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"


def load_documents():
    """
    Load all Markdown documents from the
    project knowledge directory.
    """

    if not KNOWLEDGE_DIR.is_dir():
        raise FileNotFoundError(
            f"Knowledge directory not found: {KNOWLEDGE_DIR}"
        )

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        content = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            {
                "filename": file_path.name,
                "content": content
            }
        )

    return documents


if __name__ == "__main__":

    documents = load_documents()

    print(
        f"Knowledge directory: {KNOWLEDGE_DIR}"
    )

    print(
        f"Loaded {len(documents)} documents."
    )

    for document in documents:

        print(
            f"\n--- {document['filename']} ---"
        )

        print(
            document["content"][:200]
        )