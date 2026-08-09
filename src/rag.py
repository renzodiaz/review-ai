from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    EMBEDDING_MODEL,
    TOP_K,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent / "knowledge"

def load_documents() -> list[Document]:
    """
    Load all Markdown files from the knowledge directory.
    """

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):

        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name
                },
            )
        )

    return documents


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """
    Split knowledge documents into smaller chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    return splitter.split_documents(documents)

def create_embeddings():
    """
    Create the Hugging Face embedding model.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

def build_vector_db() -> FAISS:
    """
    Build a FAISS vector database from the knowledge base.
    """

    documents = load_documents()

    if not documents:
        raise RuntimeError(
            "No knowledge documents found."
        )

    chunks = split_documents(documents)

    embeddings = create_embeddings()

    vector_db = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    return vector_db

def retrieve(
    vector_db: FAISS,
    query: str,
) -> list[Document]:
    """
    Retrieve the most relevant knowledge chunks.
    """

    return vector_db.similarity_search(
        query,
        k=TOP_K,
    )


def load_vector_db() -> FAISS:
    """
    Convenience function used by the notebook.
    """

    return build_vector_db()