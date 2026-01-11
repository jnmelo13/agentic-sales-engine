from langgraph.checkpoint.redis import RedisSaver


def get_redis_checkpointer(redis_uri: str) -> RedisSaver:
    """
    Factory function to create a Redis checkpointer.

    Args:
        redis_uri: Redis connection string

    Returns:
        RedisSaver context manager for LangGraph state persistence
    """
    return RedisSaver.from_conn_string(redis_uri)
