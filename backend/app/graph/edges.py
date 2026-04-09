from app.graph.state import AgentState

def should_execute_tool(state: AgentState):
    """Quyết định có chạy Tool Node hay rẽ nhánh Fallback"""
    retrieved = state.get("retrieved_services", [])
    if len(retrieved) > 0:
        return "tool_execution"
    return "fallback"

def should_synthesize(state: AgentState):
    """Quyết định có chạy Synthesis hay Fallback sau Tool Node"""
    results = state.get("tool_results", [])
    if len(results) > 0:
        return "llm_synthesis"
    return "fallback"
