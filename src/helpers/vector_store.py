from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

def create_vector_store_from_documents(chunks, persist_directory: str) -> Chroma:
    """
    Create a vector store from the given chunks and persist it to the specified directory.

    Args:
        chunks: List of document chunks to be stored in the vector store.
        persist_directory: Directory where the vector store will be persisted.

    Returns:
        Chroma: The created vector store.
    """
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs = {"device":"cpu"}
    )

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    return vectordb

def create_vector_store_from_texts(
    texts, persist_directory: str
) -> Chroma:
    """
    Create a vector store from the given texts and persist it to the specified directory.

    Args:
        texts: List of texts to be stored in the vector store.
        persist_directory: Directory where the vector store will be persisted.

    Returns:
        Chroma: The created vector store.
    """
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs = {"device":"cpu"}
    )

    vectordb = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        persist_directory=persist_directory,
    )

    return vectordb