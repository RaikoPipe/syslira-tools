from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_process_pdfs(data_dir: str):
    # noinspection PyTypeChecker
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.pdf",
        show_progress=True,
        loader_cls=PyPDFLoader,
    )

    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    return text_splitter.split_documents(documents)

def process_text(text: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
    )

    return text_splitter.split_text(text)

