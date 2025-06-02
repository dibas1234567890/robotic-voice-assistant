from typing import List, TypedDict, Literal
from langchain_core.tools import tool


class ServiceRequest(TypedDict):
    service_request: Literal["front_desk", "room_service", "housekeeping", "maintenance", "admin", "help"]
    quantity: int
    query: str

@tool
async def hotel_service_tool(requests: List[ServiceRequest]):
    """Takes query about the hotel services"""
    requests
    return f"The request for {requests[0]} has been processed and the hotel staff wil contact you shortly"
    
