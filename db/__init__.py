from types import CoroutineType
from typing import Any
import chromadb 
import datetime
from colorama import Fore
from chromadb import AsyncClientAPI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import os 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai_ef = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY, model_name="text-embedding-002")

class CustomChroma: 
    def __init__(self):
        pass

    async def initialize_async_chroma() -> CoroutineType[Any, Any, AsyncClientAPI]: 
        global chroma_client
        chroma_client = await chromadb.AsyncHttpClient()
        return chroma_client
    

    async def create_collection(self, filename:str, intent:str): 
        try: 
            collection = await chroma_client.create_collection(name=intent, metadata= {"time-created": str(datetime.datetime.now()), "filename":filename})
            return collection
        except Exception as e:
            print(Fore.RED + f"Error in creating Chroma collection {e}")

    
    async def add_to_collection(self, collection_name:str, documents, filename:str): 
        try: 
            collection_ = await chroma_client.get_or_create_collection(name=collection_name)
            embeddings = []
            for doc in documents: 
                embeddings.append(openai_ef(doc.page_content))
            await collection_.add(documents=documents, metadata = {"filename":filename}, embeddings=embeddings)
        except Exception as e:
            raise e
        

    async def delete_collection(collection_name:str, metadata:dict = {}): 
        try: 

            if metadata: 
                chroma_client.delete_collection(collection_name, metadata=metadata)
            else: 
                chroma_client.delete_collection(collection_name)
        except Exception as e: 
            raise e
        

    async def get_collection(collection_name:str): 
        collection_result = chroma_client.get_collection(name=collection_name)
        return collection_result