"""
Vector database configuration settings.
"""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class VectorDBSettings:
    """Configuration settings for QDrant vector database."""

    # Connection settings
    host: str = os.getenv("QDRANT_HOST", "localhost")
    port: int = int(os.getenv("QDRANT_PORT", "6333"))
    grpc_port: int = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
    prefer_grpc: bool = os.getenv("QDRANT_PREFER_GRPC", "true").lower() == "true"
    api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    https: bool = os.getenv("QDRANT_HTTPS", "false").lower() == "true"

    # Collection settings
    collection_name: str = os.getenv("QDRANT_COLLECTION", "leads-collection")
    vector_size: int = 64
    distance_metric: str = "Cosine"
    
    # Performance settings
    timeout: float = float(os.getenv("QDRANT_TIMEOUT", "10.0"))  # seconds
    batch_size: int = int(os.getenv("QDRANT_BATCH_SIZE", "100"))

    @property
    def url(self) -> str:
        """Get the QDrant server URL."""
        protocol = "https" if self.https else "http"
        return f"{protocol}://{self.host}:{self.port}"

    @classmethod
    def from_env(cls) -> "VectorDBSettings":
        """Create settings from environment variables."""
        return cls()