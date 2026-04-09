from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    user_query: str
    normalized_query: Optional[str]
    intent: Optional[str]                     # Extracted branch/intent
    action_type: Optional[str]                # "triage" | "compare_price" | "general"
    is_emergency: bool                        # Emergency detection flag
    confidence_score: float                   # Composite confidence score
    retrieved_services: List[Dict[str, Any]]  # Top-k items from Chroma
    selected_services: List[Dict[str, Any]]   # Post-filtered results
    tool_results: List[Dict[str, Any]]        # SQLite exact query results
    final_answer: str                         # Markdown answer
    debug_trace: List[Dict[str, Any]]         # Step-by-step trace for debugging
