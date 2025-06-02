from langchain_core.tools import tool

@tool
async def get_weather(city): 
    """Provide the query related to the weather of the city"""

    output_text = f"Temparature im {city} is 26C"
    return output_text