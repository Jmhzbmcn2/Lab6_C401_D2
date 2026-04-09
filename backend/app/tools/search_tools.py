from app.database.sqlite_db import query_services_by_ids, fallback_fuzzy_search
from app.utils.logger import get_logger

logger = get_logger()

def fetch_services_by_ids(ids: list, branch_filter: str) -> list[dict]:
    """Pure business logic for fetching service details based on IDs retrieved from Chroma."""
    try:
        if not ids:
            return []
        results = query_services_by_ids(ids, branch_filter=branch_filter)
        return results
    except Exception as e:
        logger.error(f"Error in fetch_services_by_ids tool: {e}")
        return []

def fallback_keyword_search(query: str, branch_filter: str) -> list[dict]:
    """Pure business logic for falling back to SQLite fuzzy search when Vector DB fails."""
    try:
        results = fallback_fuzzy_search(query, branch_filter=branch_filter)
        return results
    except Exception as e:
        logger.error(f"Error in fallback_keyword_search tool: {e}")
        return []
