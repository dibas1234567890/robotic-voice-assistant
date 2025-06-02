from .hotel_information_tools import general_hotel_information_tool
from .hotel_service_tools import hotel_service_tool
from .local_information_tools import local_information_tool
from .weather_tool import get_weather

def all_tools():
    
    tools = [general_hotel_information_tool, hotel_service_tool, local_information_tool, get_weather]

    return tools