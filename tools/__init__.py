from .hotel_information_tools import general_hotel_information_tool
from .hotel_service_tools import hotel_service_tool
from .local_information_tools import local_information_tool
from .weather_tool import get_weather

def all_tools():
    """Returns a list of all available hotel-related utility tools.

    Returns:
    List[Callable[..., Any]]: A list of callable tool function including general hotel info,
    hotel services, local information, and weather data.
    
    """
    
    tools = [general_hotel_information_tool, hotel_service_tool, local_information_tool, get_weather]

    return tools