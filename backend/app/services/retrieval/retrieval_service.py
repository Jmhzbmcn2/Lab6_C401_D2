from app.database.chroma_db import search_services
from app.utils.logger import get_logger

logger = get_logger()

def execute_vector_retrieval(query: str, intent_branch: str, top_k: int = 10) -> list[dict]:
    """Execute vector retrieval against ChromaDB."""
    try:
        results = search_services(query=query, n_results=top_k, branch=intent_branch)
        return results
    except Exception as e:
        logger.error(f"Retrieval service failed: {e}")
        return []
