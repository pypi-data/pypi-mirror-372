"""
Stash MCP Server main module.

This module provides the main entry point and core functionality for the 
Stash MCP server, including API communication and tool implementations.
"""

import asyncio
import os
import sys
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server import stdio
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

def get_auth_headers(token: str) -> dict[str, str]:
    """Get authentication headers for Stash API requests.
    
    Args:
        token: The MCP authentication token
        
    Returns:
        Dictionary containing authentication headers
        
    Raises:
        ValueError: If token is empty or None
    """
    if not token:
        raise ValueError("MCP token is not provided")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

async def make_stash_request(url: str, token: str) -> dict[str, Any] | None:
    """Make authenticated request to Stash API.
    
    Args:
        url: The API endpoint URL
        token: The MCP authentication token
        
    Returns:
        JSON response data or None if request failed
    """
    try:
        headers = get_auth_headers(token)
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error making Stash API request: {str(e)}")
        return None

def format_original_issue(issue: dict) -> str:
    """Format the original issue into a readable string.

    Args:
        issue: The original issue data

    Returns:
        Formatted string representation of the original issue
    """
    if not issue:
        return "No original issue found."

    return f"""
        Key: {issue.get('key', '<No key>')}
        Summary: {issue.get('summary', '<No title>')}
        Description: {issue.get('description', '<No description>')}
        URL: {issue.get('url', '<No URL>')}
    """

def format_similar_issues(similar_issues: list) -> str:
    """Format similar issues into a readable string.
    
    Args:
        similar_issues: List of similar issue data
        
    Returns:
        Formatted string representation of similar issues
    """
    if not similar_issues:
        return "No similar issues found."
    
    output = []
    for item in similar_issues:
        issue = item.get("issue", {})
        similarity = item.get("similarity", 0)
        if similarity < 0.70:
            continue
        output.append(f"""
• {issue.get('key', '<No key>')}: {issue.get('summary', '<No title>')}
  Description: {issue.get('description', '<No description>')}
  Similarity: {similarity:.2%}
  URL: {issue.get('url', '<No URL>')}""")
    
    return "\n".join(output)

def format_similar_documents(similar_documents: list) -> str:
    """Format similar documents into a readable string.
    
    Args:
        similar_documents: List of similar document data
        
    Returns:
        Formatted string representation of similar documents
    """
    if not similar_documents:
        return "No similar documents found."
    
    output = []
    for item in similar_documents:
        doc = item.get("document", {})
        chunks = item.get("chunks", [])
        scores = item.get("similarity_scores", [])
        if scores[0] < 0.70:
            continue
        context = f"""
        {doc.get('title', '<No title>')}
        {doc.get('url', '<No URL>')}
        """

        for i, chunk in enumerate(chunks):
            score = scores[i] if i < len(scores) else 0
            if score < 0.70:
                continue
            context += f"""
Chunk {i+1} with similarity {score:.2%}:
{chunk}
"""
        output.append(context)
    return "\n".join(output)

def format_similar_files(similar_files: list) -> str:
    """Format similar files into a readable string.
    
    Args:
        similar_files: List of similar file data
        
    Returns:
        Formatted string representation of similar files
    """
    if not similar_files:
        return "No similar code files found."
    
    output = []
    for item in similar_files:
        file = item.get("file", {})
        chunks = item.get("chunks", [])
        output.append(f"\n• {file.get('path', '<No path>')}")
        
        for chunk in chunks:
            start, end = chunk["start_end_lines"]
            score = chunk["similarity_score"]
            url = chunk.get("url", "<No URL>")
            if score < 0.60:
                continue
            output.append(f"""
  Lines {start}-{end}
  Similarity: {score:.2%}
  URL: {url}""")
    
    return "\n".join(output)

def format_experts(experts: list) -> str:
    """Format experts into a readable string.
    
    Args:
        experts: List of expert data
        
    Returns:
        Formatted string representation of experts
    """
    if not experts:
        return "No experts identified."
    
    output = []
    for expert in experts:
        user = expert.get("user", {})
        score = expert.get("score", 0)
        availability = expert.get("availability", "Unknown")
        output.append(f"""
• {user.get('name', user.get('email', '<No name>'))}
  Availability: {availability}
  Expertise Score: {score:.2%}""")
    
    return "\n".join(output)

# Initialize the MCP server
app = Server("stash-mcp-server")

# Store token globally when server starts
_mcp_token: str = ""

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_my_tasks",
            description="List all tasks assigned to the authenticated user, grouped by categories",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_issue_analysis",
            description="Get detailed analysis for a specific issue including similar content and experts",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_slug": {
                        "type": "string",
                        "description": "The project's slug identifier"
                    },
                    "issue_id": {
                        "type": "string",
                        "description": "UUID of the issue"
                    }
                },
                "required": ["project_slug", "issue_id"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    token = _mcp_token
    
    if name == "list_my_tasks":
        return await list_my_tasks(token)
    elif name == "get_issue_analysis":
        project_slug = arguments.get("project_slug")
        issue_id = arguments.get("issue_id")
        if not project_slug or not issue_id:
            return [TextContent(
                type="text",
                text="Error: Both project_slug and issue_id are required"
            )]
        return await get_issue_analysis(project_slug, issue_id, token)
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

async def list_my_tasks(token: str) -> list[TextContent]:
    """List all tasks assigned to the authenticated user, grouped by categories."""
    api_base = os.getenv("STASH_API_BASE")
    url = f"{api_base}/users/dashboard/"
    data = await make_stash_request(url, token)
    
    if not data:
        return [TextContent(
            type="text",
            text="Unable to fetch your assigned tasks. Please make sure your MCP token is set correctly."
        )]
    
    if not data.get("issues"):
        return [TextContent(
            type="text",
            text="You have no assigned tasks."
        )]
        
    output = []
    for group in data["issues"]:
        group_str = f"\n=== {group['title']} ===\n"
        
        if not group["issues"]:
            group_str += "No issues in this category\n"
        else:
            for issue in group["issues"]:
                issue_str = f"""
{issue.get('key', '<No key>')}: {issue.get('title', '<No title>')}
Issue ID: {issue.get('id', '<No ID>')}
Project Name: {issue.get('project', {}).get('name', '<Unknown>')}
Project Slug: {issue.get('project', {}).get('slug', '<Unknown>')}
"""
                group_str += issue_str
        
        output.append(group_str)
    
    return [TextContent(
        type="text",
        text="\n".join(output)
    )]

async def get_issue_analysis(project_slug: str, issue_id: str, token: str) -> list[TextContent]:
    """Get detailed analysis for a specific issue including similar content and experts."""
    api_base = os.getenv("STASH_API_BASE")
    issue_url = f"{api_base}/projects/{project_slug}/issues/{issue_id}/"
    issue_data = await make_stash_request(issue_url, token)

    if not issue_data:
        return [TextContent(
            type="text",
            text="Unable to fetch issue details. Please check your MCP token and the issue ID."
        )]

    url = f"{api_base}/projects/{project_slug}/issues/{issue_id}/analysis/"
    data = await make_stash_request(url, token)
    
    if not data:
        return [TextContent(
            type="text",
            text="Unable to fetch issue analysis. Please check your MCP token and the issue ID."
        )]
    
    sections = [
        ("Original Issue", format_original_issue(issue_data)),
        ("Similar Issues", format_similar_issues(data.get("similar_issues", []))),
        ("Similar Documents", format_similar_documents(data.get("similar_documents", []))),
        ("Similar Code Files", format_similar_files(data.get("similar_files", []))),
        ("Knowledgeable Team Members", format_experts(data.get("experts", [])))
    ]
    
    output = ["Solve Original Issue by looking at its description and the following relevant information:"]
    for title, content in sections:
        output.extend([f"\n--- {title} ---", content])
    
    return [TextContent(
        type="text",
        text="\n".join(output)
    )]

def main() -> None:
    """Main entry point for the MCP server."""
    
    async def run_server() -> None:
        global _mcp_token
        
        # Get token from environment variable
        _mcp_token = os.getenv("STASH_MCP_TOKEN", "")
        if not _mcp_token:
            print("STASH_MCP_TOKEN environment variable is not set")
            sys.exit(1)
        
        # Verify API base is set
        api_base = os.getenv("STASH_API_BASE")
        if not api_base:
            print("STASH_API_BASE environment variable is not set")
            sys.exit(1)
        
        print("Starting Stash MCP Server...")
        
        # For stdio server
        try:
            async with stdio.stdio_server() as (read_stream, write_stream):
                await app.run(
                    read_stream,
                    write_stream,
                    app.create_initialization_options()
                )
        except Exception as e:
            print(f"Server error: {e}")
            sys.exit(1)
    
    asyncio.run(run_server())

if __name__ == "__main__":
    main()
