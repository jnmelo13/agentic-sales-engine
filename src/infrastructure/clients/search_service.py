from langchain_community.utilities import GoogleSerperAPIWrapper

class WebSearchService:
    """Service for searching the web."""

    def __init__(self, api_key: str):
        """Initialize the web search service."""
        self.api_key = api_key
        self.search_engine = GoogleSerperAPIWrapper()

    def search(self, query: str) -> str:
        """Search the web for the given query."""
        return self.search_engine.run(query)
