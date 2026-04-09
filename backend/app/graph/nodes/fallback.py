from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.prompts.system_prompts import DISCLAIMER_TEXT

logger = get_logger()

def fallback_node(state: AgentState) -> dict:
    logger.info("=== Fallback Node START ===")
    final_answer = (
        "Rất tiếc, tôi không tìm thấy dịch vụ nào phù hợp với yêu cầu của bạn.\n\n"
        "Bạn có thể thử:\n"
        "- Đổi từ khóa tìm kiếm\n"
        "- Sử dụng các gợi ý nhanh bên dưới\n"
        "- Bấm **Gọi nhân viên tư vấn** để được hỗ trợ trực tiếp"
    ) + DISCLAIMER_TEXT
    
    step_trace = {
        "step": "fallback",
        "input": {},
        "output": {"message": "No results found"}
    }
    logger.debug("Executing fallback response.")
    logger.info("=== Fallback Node END ===")
    
    return {"final_answer": final_answer, "debug_trace": state.get("debug_trace", []) + [step_trace]}
