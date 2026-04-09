from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.tools.search_tools import fetch_services_by_ids, fallback_keyword_search

logger = get_logger()

def tool_execution_node(state: AgentState) -> dict:
    logger.info("=== Tool Execution Node START ===")
    retrieved = state.get("retrieved_services", [])
    intent = state.get("intent", "")
    normalized_query = state.get("normalized_query", "")
    
    # Filter out items with very bad distance (> 0.6)
    valid_retrieved = [r for r in retrieved if r.get('distance', 0) < 0.6]
    
    result_ids = list(set([r["id"] for r in valid_retrieved]))
    logger.debug(f"Input IDs to query SQLite after thresholding: {len(result_ids)}")
    
    tool_results = []
    
    if result_ids:
        tool_results = fetch_services_by_ids(result_ids, branch_filter=intent)
        logger.debug(f"SQLite returned {len(tool_results)} exact tool matches from Chroma")
        
    # Fallback keyword search if chroma returned nothing or threshold blocked it
    if not tool_results:
        logger.warning("No valid results from ChromaDB. Engaging SQLite Fuzzy Fallback.")
        tool_results = fallback_keyword_search(normalized_query, branch_filter=intent)
        logger.debug(f"Fuzzy fallback returned {len(tool_results)} exact tool matches")

    step_trace = {
        "step": "tool_execution",
        "input": {"ids_count": len(result_ids), "intent": intent, "chroma_valid": len(valid_retrieved)},
        "output": {"tool_results_count": len(tool_results), "tool_results": tool_results}
    }
    
    logger.info("=== Tool Execution Node END ===")
    return {"tool_results": tool_results, "debug_trace": state.get("debug_trace", []) + [step_trace]}
