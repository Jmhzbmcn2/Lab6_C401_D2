from app.graph.state import AgentState
from app.utils.logger import get_logger

logger = get_logger()

def fallback_node(state: AgentState) -> dict:
    logger.info("=== Fallback Node START ===")
    final_answer = "Rất tiếc, tôi không tìm thấy dịch vụ nào phù hợp với yêu cầu của bạn hoặc Hệ thống không có thông tin. Bạn có thể thử đổi từ khóa khác."
    
    step_trace = {
        "step": "fallback",
        "input": {},
        "output": {"message": final_answer}
    }
    logger.debug("Executing fallback response.")
    logger.info("=== Fallback Node END ===")
    
    return {"final_answer": final_answer, "debug_trace": state.get("debug_trace", []) + [step_trace]}
