from mcp.server.fastmcp import FastMCP
import requests
import os
from typing import List, Dict, Any, Optional
import mcp.types as types

mcp = FastMCP("Demo")

HOST = os.getenv("HOST", "http://9.223.220.100")

@mcp.tool()
def get_transcript(folder_id: str, conversation_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Retrieve/get transcription content based on Conversation IDs.

     Args:
        folder_id: id of the folder where transcription files are saved
        conversation_ids: List of conversation ids or ´None'. 'None' is to return all conversations that belong to stated folder.

    Returns:
        A dictionary containing success status and a message
    """

    response = requests.get(
        url=f"{HOST}/get_transcript",
        params={
            "folder_id": folder_id,
            "conversation_ids": conversation_ids
        },
        headers={
            "Content-Type": "application/json"
        },
    )

    return response.json()

@mcp.tool()
def get_example_transcript() -> Dict[str, Any]:
    """Retrieve/get example transcription.

    Returns:
        A dictionary containing success status and a message
    """

    response = requests.get(
        url=f"{HOST}/get_example_transcript",
        headers={
            "Content-Type": "application/json"
        },
    )

    return response.json()

@mcp.tool()
def generate_transcription(conversation_ids: List[str], folder_id: Optional[str] = None) -> Dict[str, Any] | list[types.TextContent]:
    """Generate transcription based on Conversation IDs to get communication ids.
    Transcription is saved to files.

     Args:
        conversation_ids: List of conversation ids
        folder_id: id of the folder where transcription files are saved

    Returns:
        A dictionary containing success status and a message
    """

    response = requests.get(
        url=f"{HOST}/generate_transcription/",
        params={
            "conversation_ids": conversation_ids,
            "folder_id": folder_id
        },
        headers={
            "Content-Type": "application/json"
        },
    )

    return response.json()

@mcp.tool()
def interval_conversations(start: str, end: str) -> str:
    """Getting conversations happened in Genesys during provided interval.
    This requires connection authentication to Genesys to be able to call its apis.
    if it errors due to authentication, get authentication then try again.

    Args:
        start: Start of interval as year-month-day hour:minute:second (2025-05-14 13:00:00)
        end: End of interval as year-month-day hour:minute:second (2025-05-14 13:00:00)

    Returns:
        List of conversation ids happened during the provided interval.
    """

    response = requests.get(
        url=f"{HOST}/interval_conversations/{start}/{end}",
        headers={
            "Content-Type": "application/json"
        },
    )

    return response.json()

def main():
    print("Hello from transcription-mcp!")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()