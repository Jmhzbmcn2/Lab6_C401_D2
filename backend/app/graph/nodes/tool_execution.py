from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.tools.search_tools import fetch_services_by_ids, fallback_keyword_search

logger = get_logger()

def tool_execution_node(state: AgentState) -> dict:
    logger.info("=== Tool Execution Node START ===")
    retrieved = state.get("retrieved_services", [])
    intent = state.get("intent", "")
    normalized_query = state.get("normalized_query", "")
    
    # Compute composite confidence score
    if retrieved:
        distances = [r.get('distance', 1.0) for r in retrieved[:5]]
        avg_distance = sum(distances) / len(distances)
        # Convert distance to similarity (lower distance = higher confidence)
        vector_similarity = max(0, 1 - avg_distance)
        
        # Symptom match: how many of the top results have low distance
        good_matches = sum(1 for d in distances if d < 0.4)
        symptom_match_score = good_matches / len(distances)
        
        # Intent clarity: if we have a clear branch intent
        intent_clarity_score = 1.0 if intent else 0.5
        
        confidence_score = round(
            0.5 * vector_similarity + 
            0.3 * symptom_match_score + 
            0.2 * intent_clarity_score, 
            3
        )
    else:
        confidence_score = 0.0

    logger.debug(f"Confidence Score: {confidence_score}")
    
    # Filter out items with very bad distance (> 0.6)
    valid_retrieved = [r for r in retrieved if r.get('distance', 0) < 0.6]
    
    result_ids = list(set([r["id"] for r in valid_retrieved]))
    logger.debug(f"Input IDs to query SQLite after thresholding: {len(result_ids)}")
    
    tool_results = []
    try:
        if result_ids:
            tool_results = fetch_services_by_ids(result_ids, branch_filter=intent)
            logger.debug(f"SQLite returned {len(tool_results)} exact tool matches from Chroma")
            
        # Fallback keyword search if chroma returned nothing or threshold blocked it
        if not tool_results:
            logger.warning("No valid results from ChromaDB. Engaging SQLite Fuzzy Fallback.")
            tool_results = fallback_keyword_search(normalized_query, branch_filter=intent)
            logger.debug(f"Fuzzy fallback returned {len(tool_results)} exact tool matches")
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        
    step_trace = {
        "step": "tool_execution",
        "input": {"ids_count": len(result_ids), "intent": intent, "chroma_valid": len(valid_retrieved)},
        "output": {
            "tool_results_count": len(tool_results), 
            "confidence_score": confidence_score,
            "tool_results": tool_results
        }
    }
    
    logger.info("=== Tool Execution Node END ===")
    return {
        "tool_results": tool_results, 
        "confidence_score": confidence_score,
        "debug_trace": state.get("debug_trace", []) + [step_trace]
    }
