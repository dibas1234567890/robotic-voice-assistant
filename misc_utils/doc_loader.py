from custom_db.chroma_async_client import CustomChroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

async def doc_loader_(file_path:str, choice:str = "pdf"): 
    pdf_loader = PyPDFLoader(file_path=file_path)
    docs = pdf_loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size =500, 
                                                   chunk_overlap = 100)
    splits = text_splitter.split_documents(docs)

    return splits
