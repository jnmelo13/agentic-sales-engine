import os

from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_mcp_client():
    client = MultiServerMCPClient(
        {
            "google_workspace": {
                "transport": "streamable_http",
                "url": f"{os.getenv('WORKSPACE_MCP_BASE_URI', 'http://localhost')}:{os.getenv('WORKSPACE_MCP_PORT', '8001')}/mcp",
            }
        }
    )
    return client