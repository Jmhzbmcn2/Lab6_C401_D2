from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.services.retrieval.retrieval_service import execute_vector_retrieval

logger = get_logger()

def retrieval_node(state: AgentState) -> dict:
    logger.info("=== Retrieval Node START ===")
    query = state.get("normalized_query", state.get("user_query", ""))
    intent = state.get("intent", "")
    logger.debug(f"Query: {query} | Intent: {intent}")
    
    queries = [q.strip() for q in query.split(',')] if ',' in query else [query]
    all_retrieved = []
    
    try:
        for q in queries:
            if not q: continue
            results = execute_vector_retrieval(query=q, intent_branch=intent, top_k=10)
            all_retrieved.extend(results)
            logger.debug(f"Retrieved {len(results)} services for '{q}'")
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        
    step_trace = {
        "step": "retrieval",
        "input": {"queries": queries, "intent": intent},
        "output": {"retrieved_count": len(all_retrieved), "retrieved_ids": [r["id"] for r in all_retrieved]}
    }
    
    logger.info("=== Retrieval Node END ===")
    return {"retrieved_services": all_retrieved, "debug_trace": state.get("debug_trace", []) + [step_trace]}
