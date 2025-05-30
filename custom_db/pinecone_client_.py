import os
from pinecone import PineconeAsyncio, ServerlessSpec

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

class PineconeCustom:
    def __init__(self, api_key: str = PINECONE_API_KEY):
        self.api_key = api_key
        self.pc = None
        self.index = None

    async def __aenter__(self):
        self.pc = PineconeAsyncio(api_key=self.api_key)
        await self.pc.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.pc.__aexit__(exc_type, exc, tb)

    async def list_indexes(self):
        return await self.pc.list_indexes()

    async def create_index(self, index_name: str, dimension: int = 1024):
        exists = await self.pc.has_index(index_name)
        if not exists:
            await self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                deletion_protection="disabled",
                tags={"environment": "development"}
            )

    async def connect_index(self, index_name: str):
        self.index = self.pc.IndexAsyncio("https://default-index-vvouc9f.svc.aped-4627-b74a.pinecone.io")

    async def upsert_vectors(self, items, namespace: str = "default"):
        """
        Upserts a list of vectors into Pinecone.
        
        Args:
            items (list): List of tuples (id, vector, metadata?) like:
                [
                    ("id1", [0.1, 0.2, ...], {"text": "doc1"}),
                    ("id2", [0.3, 0.4, ...], {"text": "doc2"}),
                ]
            namespace (str): Optional Pinecone namespace.
        """
        if self.index is None:
            raise ValueError("Index not connected. Call connect_index() first.")

        await self.index.upsert(vectors=items, namespace=namespace)

    async def similarity_search(self, vector, top_k=5, namespace="default"):
        if self.index is None:
            raise ValueError("Index not connected. Call connect_index() first.")
        return await self.index.query(vector=vector, top_k=top_k, namespace=namespace, include_metadata=True)
