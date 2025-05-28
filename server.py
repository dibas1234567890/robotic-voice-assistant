# built-in imports
import os
import shutil
from fastapi import FastAPI, File, UploadFile
import uvicorn
from contextlib import asynccontextmanager

# custom imports
from misc_utils.doc_loader import doc_loader_
from misc_utils.unique_id_generator import unique_id_gen
from custom_db import CustomChroma

TEMP_STORAGE_PATH = os.getenv("TEMP_STORAGE_PATH", "/tmp")  

chroma_client = CustomChroma()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await chroma_client.initialize_async_chroma()
    yield  


app = FastAPI(lifespan=lifespan)


@app.post("/doc-loader")
async def load_docs(file: UploadFile = File(...), intent: str = "default_collection"):
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
        await chroma_client.add_to_collection(
            collection_name=intent,
            documents=splits,
            filename=file.filename
        )

        return {"message": "Successfully uploaded and stored docs"}

    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if pdf_dir and os.path.exists(pdf_dir):
            shutil.rmtree(pdf_dir)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
