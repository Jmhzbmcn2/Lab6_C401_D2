from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes import (
    emergency_check_node,
    query_understanding_node,
    compare_price_node,
    retrieval_node,
    tool_execution_node,
    llm_synthesis_node,
    clarification_node,
    fallback_node
)
from app.utils.logger import get_logger

logger = get_logger()

def route_after_emergency(state: AgentState):
    """Nếu cấp cứu → END, nếu không → tiếp tục query understanding."""
    if state.get("is_emergency", False):
        return "end_emergency"
    return "query_understanding"

def route_after_understanding(state: AgentState):
    """Phân luồng: so sánh giá hoặc tra cứu bình thường."""
    action_type = state.get("action_type", "triage")
    if action_type == "compare_price":
        return "compare_price"
    return "retrieval"

def should_execute_tool(state: AgentState):
    """Quyết định có chạy Tool Node hay rẽ nhánh Fallback."""
    retrieved = state.get("retrieved_services", [])
    if len(retrieved) > 0:
        return "tool_execution"
    return "fallback"

def route_after_tool(state: AgentState):
    """Quyết định: Synthesis, Clarification, hay Fallback sau Tool Node."""
    results = state.get("tool_results", [])
    confidence = state.get("confidence_score", 0.0)
    
    if len(results) == 0:
        return "fallback"
    
    # If confidence is very low, ask for clarification instead of synthesizing
    if confidence < 0.25 and len(results) > 0:
        return "clarification"
    
    return "llm_synthesis"

def build_graph():
    logger.info("Building LangGraph v2 (with Emergency, Compare, Clarification)...")
    
    workflow = StateGraph(AgentState)

    # 1. Add all nodes
    workflow.add_node("emergency_check", emergency_check_node)
    workflow.add_node("query_understanding", query_understanding_node)
    workflow.add_node("compare_price", compare_price_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("llm_synthesis", llm_synthesis_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("fallback", fallback_node)

    # 2. Edges: START → emergency_check
    workflow.add_edge(START, "emergency_check")
    
    # 3. After emergency check: either end (emergency) or continue
    workflow.add_conditional_edges(
        "emergency_check",
        route_after_emergency,
        {
            "end_emergency": END,
            "query_understanding": "query_understanding"
        }
    )
    
    # 4. After understanding: compare_price or normal retrieval
    workflow.add_conditional_edges(
        "query_understanding",
        route_after_understanding,
        {
            "compare_price": "compare_price",
            "retrieval": "retrieval"
        }
    )
    
    # 5. Compare price goes straight to END
    workflow.add_edge("compare_price", END)
    
    # 6. After retrieval: tool_execution or fallback
    workflow.add_conditional_edges(
        "retrieval",
        should_execute_tool,
        {
            "tool_execution": "tool_execution",
            "fallback": "fallback"
        }
    )
    
    # 7. After tool execution: synthesis, clarification, or fallback
    workflow.add_conditional_edges(
        "tool_execution",
        route_after_tool,
        {
            "llm_synthesis": "llm_synthesis",
            "clarification": "clarification",
            "fallback": "fallback"
        }
    )

    # 8. Terminal edges
    workflow.add_edge("llm_synthesis", END)
    workflow.add_edge("clarification", END)
    workflow.add_edge("fallback", END)

    app = workflow.compile()
    logger.info("LangGraph v2 built successfully.")
    return app

graph_app = build_graph()
