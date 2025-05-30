from custom_db.pinecone_client_ import PineconeCustom
import os 

INDEX = os.getenv("INDEX")
pinecone_client = PineconeCustom()

async def local_information_tool():
    await pinecone_client.__aenter__()
    pass