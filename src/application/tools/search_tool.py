from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool


def create_search_tool() -> Tool:
    """Create search tool for company information."""
    serper_search = GoogleSerperAPIWrapper()

    return Tool(
        name="search_company_info",
        description=(
            "Search the web for detailed information about a company including recent news, "
            "technologies used, partnerships, and business updates. "
            "Use this when you need more context about a lead company."
        ),
        func=serper_search.run,
    )

