from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes.query_understanding import query_understanding_node
from app.graph.nodes.retrieval import retrieval_node
from app.graph.nodes.tool_execution import tool_execution_node
from app.graph.nodes.synthesis import llm_synthesis_node
from app.graph.nodes.fallback import fallback_node
from app.graph.edges import should_execute_tool, should_synthesize
from app.utils.logger import get_logger

logger = get_logger()

def build_graph():
    logger.info("Building LangGraph...")
    
    workflow = StateGraph(AgentState)

    # 1. Add nodes
    workflow.add_node("query_understanding", query_understanding_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("tool_execution", tool_execution_node)
    workflow.add_node("llm_synthesis", llm_synthesis_node)
    workflow.add_node("fallback", fallback_node)

    # 2. Add edges
    workflow.add_edge(START, "query_understanding")
    workflow.add_edge("query_understanding", "retrieval")
    
    # Conditional logic
    workflow.add_conditional_edges(
        "retrieval",
        should_execute_tool,
        {
            "tool_execution": "tool_execution",
            "fallback": "fallback"
        }
    )
    
    workflow.add_conditional_edges(
        "tool_execution",
        should_synthesize,
        {
            "llm_synthesis": "llm_synthesis",
            "fallback": "fallback"
        }
    )

    workflow.add_edge("llm_synthesis", END)
    workflow.add_edge("fallback", END)

    app = workflow.compile()
    logger.info("LangGraph built successfully.")
    return app

graph_app = build_graph()
