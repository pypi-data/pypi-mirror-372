
import logging
from re import T
from typing import Optional, Dict, List, TypedDict

from fastmcp import FastMCP
from omnidimension import Client
import os

logger = logging.getLogger(__name__)

mcp = FastMCP(name="Omnidimension MCP Server")

class TContextBreakdown(TypedDict):
    title: str
    body: str


@mcp.tool(description="for creating a new assistant")
def dispatch_a_call(assistant_id: int, to_number: str, call_context: dict) -> Dict:
    """
    Dispatch a call to given number
    params: 
        assistant_id: id of the assistant 
        to_number: a valid phone number
        call_context: a dict which contain information about whom we are calling to and purpose. like { 'caller_name': 'John Doe', 'purpose': 'appointment' }
    Returns: 
        - success 
    """
    return get_client().call.dispatch_call(agent_id=assistant_id, call_context=call_context, to_number=to_number)


@mcp.tool(description="for creating a new assistant")
def create_assistant(name: str, context_breakdown: List[TContextBreakdown], welcome_message: str) -> Dict:
    """
    params: 
    assistant_id: id of the assistant
    context_breakdown: 
            [{
            title: title of section, 
            body: prompt for assistant for this section.
            }]
    welcome_message: first message that played when agent called
    Returns: 
    - details of the assistant
    """
    return get_client().agent.create(name=name, context_breakdown=context_breakdown,welcome_message=welcome_message)


@mcp.resource("assistants://{page}/{page_size}")
def get_all_assistants(page=1, page_size=20) -> Dict:
    """Get a All available assistants
    
    params: 
    page: number of page.
    page_size: number of assistant per page.

    Returns: 
    - list of assistants
    """
    return get_client().agent.list(page=page, page_size=page_size)

@mcp.resource("assistants://{assistant_id}")
def get_assistant_details(assistant_id = int) -> Dict:
    """Get assistant's details
    
    params: 
    assistant_id: id of the assistant
    Returns: 
    - details of the assistant
    """
    return get_client().agent.get(agent_id=assistant_id)

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def get_client() -> Client:
    API_KEY = os.getenv(f"OMNIDIMENSION_API_KEY")
    return Client(api_key=API_KEY)


def create_app():
    mcp.run(transport='stdio')