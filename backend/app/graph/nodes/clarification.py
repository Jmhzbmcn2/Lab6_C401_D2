from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.prompts.system_prompts import DISCLAIMER_TEXT

logger = get_logger()

def clarification_node(state: AgentState) -> dict:
    logger.info("=== Clarification Node START ===")
    normalized_query = state.get("normalized_query", "")
    confidence_score = state.get("confidence_score", 0.0)
    
    final_answer = (
        f"## 🤔 Tôi chưa chắc chắn lắm...\n\n"
        f"Truy vấn **\"{normalized_query}\"** cho kết quả độ tự tin khá thấp ({confidence_score:.0%}).\n\n"
        f"Để giúp bạn chính xác hơn, vui lòng thử:\n"
        f"- Mô tả cụ thể hơn dịch vụ bạn cần (VD: *\"siêu âm thai 4D\"* thay vì *\"siêu âm\"*)\n"
        f"- Chỉ rõ chi nhánh (VD: *\"tại Times City\"*)\n"
        f"- Hoặc bấm nút **Gọi nhân viên tư vấn** bên dưới để được hỗ trợ trực tiếp.\n"
    ) + DISCLAIMER_TEXT
    
    step_trace = {
        "step": "clarification",
        "input": {"normalized_query": normalized_query, "confidence_score": confidence_score},
        "output": {"action": "ask_user_to_clarify"}
    }
    
    logger.info("=== Clarification Node END ===")
    return {"final_answer": final_answer, "debug_trace": state.get("debug_trace", []) + [step_trace]}
