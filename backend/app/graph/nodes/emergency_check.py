from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.prompts.system_prompts import EMERGENCY_KEYWORDS, EMERGENCY_RESPONSE

logger = get_logger()

def emergency_check_node(state: AgentState) -> dict:
    logger.info("=== Emergency Check Node START ===")
    user_query = state.get("user_query", "").lower()
    debug_trace = state.get("debug_trace", [])
    
    is_emergency = False
    matched_keywords = []
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in user_query:
            is_emergency = True
            matched_keywords.append(keyword)
    
    step_trace = {
        "step": "emergency_check",
        "input": {"user_query": user_query},
        "output": {"is_emergency": is_emergency, "matched_keywords": matched_keywords}
    }
    
    result = {
        "is_emergency": is_emergency,
        "debug_trace": debug_trace + [step_trace]
    }
    
    if is_emergency:
        logger.warning(f"🚨 EMERGENCY DETECTED. Keywords: {matched_keywords}")
        result["final_answer"] = EMERGENCY_RESPONSE
    
    logger.info("=== Emergency Check Node END ===")
    return result
