from typing import List, TypedDict, Literal
from langchain_core.tools import tool


class ServiceRequest(TypedDict):
    service_request: Literal["front_desk", "room_service", "housekeeping", "maintenance", "admin", "help"]
    quantity: int
    query: str

@tool
async def hotel_service_tool(requests: List[ServiceRequest])-> str:
    """Takes the order from the user and returns a message justifying the order.
    Args:
    requests(List[ServiceRequest]):List of dictionaries where each dictionary contains:
    service request, quantity and query

    Returns:
    str: Message confirming that the service request has been processed.
    
    """
    requests
    return f"The request for {requests[0]} has been processed and the hotel staff wil contact you shortly"
    
