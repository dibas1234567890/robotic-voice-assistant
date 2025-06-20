from langchain_core.tools import tool

@tool
async def general_hotel_information_tool(pinecone_client, query:str, intent:str = "hotel_information", )-> list[str]:
    """Takes in the query from the user only related to the hotel's information and then returns the similar answers using ChromaDB
    (Args)
        - query:str - The actual query of the user 

    Returns:
    list: A list of string containing text result relevant to the user's hotel-related query.

    """ 
    
    embbedding = await pinecone_client.pc.inference.embed(model="llama-text-embed-v2", inputs =[query], 
                                                                    parameters ={"input_type": "passage", "truncate": "END"})
    results = await pinecone_client.similarity_search(vector=embbedding.data[0]["values"], namespace=intent)

    texts = [item['metadata']['text'] for item in results['matches']]

    return texts
