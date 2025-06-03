# built-in imports
import os
import shutil
from typing import Literal
from fastapi import FastAPI, File, Form, UploadFile
import uvicorn
from contextlib import asynccontextmanager
from pydantic import BaseModel

# custom imports
from misc_utils.doc_loader import doc_loader_
from misc_utils.unique_id_generator import unique_id_gen
from custom_db.chroma_async_client import CustomChroma #can use async chroma if required
from custom_db.pinecone_client_ import PineconeCustom
from misc_utils.tuple_maker_ import prepare_upsert_tuples
from llm_utils.agents_ import agent_executor
from schema.ChatRequest import ChatRequest

TEMP_STORAGE_PATH = os.getenv("TEMP_STORAGE_PATH", "/tmp")  

# chroma_client = CustomChroma()
pinecone_client_async = PineconeCustom()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pinecone_client_async.__aenter__()
    yield  
    await pinecone_client_async.__aexit__()


app = FastAPI(lifespan=lifespan)


@app.post("/doc-loader")
async def load_docs(file: UploadFile = File(...), intent: Literal["default_collection", "hotel_information", "local_information", "pricings"] = Form(...)):
    """Endpoint to upload and process PDF for RAG"""
    pdf_dir = ""
    try:
        if file.filename.split(".")[-1].lower() != "pdf":
            return {"error": "Only PDFs are supported"}

        unique_path = unique_id_gen()
        pdf_dir = os.path.join(TEMP_STORAGE_PATH, unique_path)
        pdf_path = os.path.join(pdf_dir, file.filename)

        os.makedirs(pdf_dir, exist_ok=True)
        with open(pdf_path, "wb") as out:
            shutil.copyfileobj(file.file, out)

        splits = await doc_loader_(pdf_path)
        embeddings = await pinecone_client_async.pc.inference.embed(model="llama-text-embed-v2", inputs =[split.page_content for split in splits], 
                                                                    parameters ={"input_type": "passage", "truncate": "END"})
        items = await prepare_upsert_tuples(splits=splits, embeddings=embeddings)
        await pinecone_client_async.connect_index("default")
        await pinecone_client_async.upsert_vectors(namespace=intent, items=items)

        return {"message": "Successfully uploaded and stored docs"}

    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if pdf_dir and os.path.exists(pdf_dir):
            shutil.rmtree(pdf_dir)


@app.post("/chat-bot")
async def chat(payload:ChatRequest):
    """Endpoint to handle general queries.
    
    Parameters:
    payloaad(ChatRequst): Request body containing the user's question and session ID

    Returns:
    dict: Contains the response from the agent or an error message.  
    """
    try:

        data ={"query":payload.question, "sender_id":payload.session_id}
        
        response = await agent_executor.ainvoke(data)
        return{"response":response}
    except Exception as e:
        return{"error": str(e)}




if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
