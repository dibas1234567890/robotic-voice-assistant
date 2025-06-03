from custom_db.pinecone_client_ import PineconeCustom
import os 
from langchain_core.tools import tool

INDEX = os.getenv("INDEX")
pinecone_client = PineconeCustom()
@tool
async def local_information_tool():
    """Processes a query about local hotel services and returns relevant information.
    
    """

    await pinecone_client.__aenter__()
    pass