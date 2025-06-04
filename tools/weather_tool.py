from langchain_core.tools import tool

@tool
async def get_weather(city: str)-> str: 
    """Provide the query related to the weather of the city

    Parameters:
    city(str): Name of the city to retrieve info for.

    Returns:
    str: A string describing the temperature in the specified city
    
    """

    output_text = f"Temparature im {city} is 26C"
    return output_text