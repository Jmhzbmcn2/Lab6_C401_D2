from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.services.llm.llm_service import call_llm
from app.prompts.system_prompts import SYNTHESIS_PROMPT, DISCLAIMER_TEXT
from app.graph.nodes.fallback import fallback_node

logger = get_logger()

def llm_synthesis_node(state: AgentState) -> dict:
    logger.info("=== LLM Synthesis Node START ===")
    tool_results = state.get("tool_results", [])
    user_query = state.get("user_query", "")
    confidence_score = state.get("confidence_score", 0.0)
    
    if not tool_results:
        return fallback_node(state)
        
    # Tạo text tổng hợp
    context_lines = []
    for r in tool_results:
        price_str = f"{r['price']:,.0f} VND" if isinstance(r['price'], (int, float)) else str(r['price'])
        context_lines.append(f"- Chi nhánh: {r['branch']} | Dịch vụ: {r['service_name_vn']} | Nhóm: {r['service_group']} | Giá tiền: {price_str}")
        
    context_text = "\n".join(context_lines)
    
    # Confidence-aware phrasing
    confidence_note = ""
    if confidence_score < 0.4:
        confidence_note = "\n⚠️ LƯU Ý: Độ chính xác tìm kiếm cho truy vấn này hơi thấp. Kết quả dưới đây có thể chưa hoàn toàn phù hợp. Vui lòng kiểm tra hoặc liên hệ nhân viên tư vấn."
    
    prompt = f"Thông Tin Được Cho (Từ Cơ Sở Dữ Liệu):\n---\n{context_text}\n---\n\nCâu hỏi người dùng: {user_query}\nTrợ lý trả lời:"
    
    logger.debug(f"Calling LLM with {len(tool_results)} context items. Confidence: {confidence_score}")
    try:
        final_answer = call_llm(prompt=prompt, system_prompt=SYNTHESIS_PROMPT)
        final_answer = confidence_note + "\n" + final_answer + DISCLAIMER_TEXT
        logger.debug(f"LLM Synthesis succeeded. Output length: {len(final_answer)}")
    except Exception as e:
        logger.error(f"LLM Synthesis failed: {e}")
        final_answer = "Xin lỗi, đã xảy ra lỗi trong quá trình tổng hợp kết quả (LLM Error)." + DISCLAIMER_TEXT
        
    step_trace = {
        "step": "llm_synthesis",
        "input": {"context_items": len(tool_results), "confidence_score": confidence_score},
        "output": {"answer_length": len(final_answer)}
    }
    
    logger.info("=== LLM Synthesis Node END ===")
    return {"final_answer": final_answer, "debug_trace": state.get("debug_trace", []) + [step_trace]}
