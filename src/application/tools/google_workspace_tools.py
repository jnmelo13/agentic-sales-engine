import asyncio
from typing import Any, List

from langchain_core.tools import BaseTool, StructuredTool

from src.infrastructure.mcp_clients.client import get_mcp_client


def wrap_async_tool_for_sync(async_tool: BaseTool) -> StructuredTool:
    """Wrap an async-only MCP tool to support synchronous invocation.
    
    MCP tools from langchain-mcp-adapters only implement _arun (async).
    This wrapper adds sync support by running the async method in a new event loop.
    
    Args:
        async_tool: Async-only tool from MCP client
        
    Returns:
        StructuredTool with both sync and async support
    """
    async def async_func(*args: Any, **kwargs: Any) -> Any:
        """Async version - delegates to original tool."""
        # Extract config from kwargs (required by LangChain tools)
        config = kwargs.pop('config', None)
        if config is None:
            from langchain_core.runnables import RunnableConfig
            config = RunnableConfig()
        return await async_tool._arun(*args, config=config, **kwargs)
    
    def sync_func(*args: Any, **kwargs: Any) -> Any:
        """Sync version - runs async in new event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(async_func(*args, **kwargs))
        finally:
            loop.close()
    
    return StructuredTool(
        name=async_tool.name,
        description=async_tool.description,
        func=sync_func,  # Sync execution
        coroutine=async_func,  # Async execution
        args_schema=async_tool.args_schema,
    )


def get_google_workspace_tools_sync() -> List[BaseTool]:
    """Fetch Google Workspace tools from MCP server with graceful fallback.
    
    Returns:
        List of filtered Google Workspace tools (Sheets, Drive) wrapped for sync support,
        or empty list if unavailable.
    """
    async def _fetch_tools() -> List[BaseTool]:
        client = await get_mcp_client()
        mcp_tools = await client.get_tools()
        
        # Filter to only specific tools needed for spreadsheet and drive operations
        allowed_tools = {
            'list_spreadsheets',
            'read_sheet_values',
            'get_drive_file_content',
            'list_drive_items',
            'search_drive_files'
        }
        
        filtered_tools = [
            tool for tool in mcp_tools 
            if tool.name in allowed_tools
        ]
        
        # Wrap filtered MCP tools to support sync invocation
        return [wrap_async_tool_for_sync(tool) for tool in filtered_tools]
    
    try:
        tools = asyncio.run(_fetch_tools())
        print(f"✓ Loaded {len(tools)} Google Workspace tools (filtered and wrapped for sync support)")
        return tools
    except Exception as e:
        print(f"⚠ Could not load Google Workspace tools: {e}")
        return []