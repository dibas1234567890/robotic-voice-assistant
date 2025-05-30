import os
import datetime
from colorama import Fore
from chromadb import AsyncClientAPI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import chromadb
import uuid

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_ef = OpenAIEmbeddingFunction(api_key=OPENAI_API_KEY)


class CustomChroma:
    def __init__(self):
        self.chroma_client: AsyncClientAPI = None

    async def initialize_async_chroma(self) -> AsyncClientAPI:
        self.chroma_client = await chromadb.AsyncHttpClient(host="localhost", port=1697)
        return self.chroma_client

    async def create_collection(self, filename: str, intent: str):
        try:
            collection = await self.chroma_client.create_collection(
                name=intent,
                metadata={
                    "time-created": str(datetime.datetime.now()),
                    "filename": filename,
                }
            )
            return collection
        except Exception as e:
            print(Fore.RED + f"Error in creating Chroma collection: {e}")
            print(Fore.BLACK)


    async def add_to_collection(self, collection_name: str, documents, filename: str):
        try:
            collection_ = await self.chroma_client.get_or_create_collection(name=collection_name)
            texts = [doc.page_content for doc in documents]
            embeddings = openai_ef(texts)

            # Generate unique IDs
            ids = [str(uuid.uuid4()) for _ in texts]

            # Repeat metadata for each document
            metadatas = [{"filename": filename, "date-created": datetime.datetime.now().isoformat()} for _ in texts]

            await collection_.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas,
                embeddings=embeddings
            )
        except Exception as e:
            raise e


    async def delete_collection(self, collection_name: str, metadata: dict = {}):
        try:
            if metadata:
                await self.chroma_client.delete_collection(collection_name, metadata=metadata)
            else:
                await self.chroma_client.delete_collection(collection_name)
        except Exception as e:
            raise e

    async def get_collection(self, collection_name: str):
        try:
            return await self.chroma_client.get_collection(name=collection_name)
        except Exception as e:
            raise e
