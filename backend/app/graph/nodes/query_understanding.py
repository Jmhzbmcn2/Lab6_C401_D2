import json
from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.services.llm.llm_service import call_llm_structured
from app.prompts.system_prompts import QUERY_UNDERSTANDING_PROMPT
from app.schemas.api_models import IntentSchema

logger = get_logger()

def query_understanding_node(state: AgentState) -> dict:
    logger.info("=== Query Understanding Node START ===")
    user_query = state.get("user_query", "")
    logger.debug(f"Input User Query: {user_query}")
    
    debug_trace = state.get("debug_trace", [])
    
    try:
        raw_json = call_llm_structured(prompt=user_query, schema_class=IntentSchema, system_prompt=QUERY_UNDERSTANDING_PROMPT)
        
        parsed = json.loads(raw_json)
        normalized_query = parsed.get("normalized_query", user_query)
        intent = parsed.get("intent_branch", "")
        action_type = parsed.get("action_type", "triage")
            
        logger.debug(f"Normalized Query: {normalized_query} | Intent: {intent} | Action: {action_type}")
        
    except Exception as e:
        logger.error(f"Query understanding failed: {e}")
        normalized_query = user_query
        intent = ""
        action_type = "triage"

    step_trace = {
        "step": "query_understanding",
        "input": {"user_query": user_query},
        "output": {"normalized_query": normalized_query, "intent": intent, "action_type": action_type}
    }
    
    logger.info("=== Query Understanding Node END ===")
    return {
        "normalized_query": normalized_query,
        "intent": intent,
        "action_type": action_type,
        "debug_trace": debug_trace + [step_trace]
    }
