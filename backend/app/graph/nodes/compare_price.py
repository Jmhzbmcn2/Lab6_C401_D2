from app.graph.state import AgentState
from app.utils.logger import get_logger
from app.services.llm.llm_service import call_llm
from app.prompts.system_prompts import COMPARE_PRICE_PROMPT, DISCLAIMER_TEXT
from app.database.sqlite_db import compare_services_across_branches

logger = get_logger()

def compare_price_node(state: AgentState) -> dict:
    logger.info("=== Compare Price Node START ===")
    normalized_query = state.get("normalized_query", "")
    user_query = state.get("user_query", "")
    debug_trace = state.get("debug_trace", [])
    
    results = compare_services_across_branches(normalized_query)
    logger.debug(f"Compare query returned {len(results)} results")

    if not results:
        step_trace = {
            "step": "compare_price",
            "input": {"normalized_query": normalized_query},
            "output": {"count": 0, "message": "No results found"}
        }
        final_answer = f"Rất tiếc, tôi không tìm thấy dịch vụ **\"{normalized_query}\"** trong cơ sở dữ liệu để so sánh. Bạn có thể thử từ khóa khác hoặc liên hệ tư vấn viên." + DISCLAIMER_TEXT
        return {"final_answer": final_answer, "tool_results": [], "debug_trace": debug_trace + [step_trace]}
    
    # Group by branch
    branch_data = {}
    for r in results:
        branch = r["branch"]
        if branch not in branch_data:
            branch_data[branch] = []
        branch_data[branch].append(r)
    
    # Build comparison context
    context_lines = []
    for branch, services in branch_data.items():
        context_lines.append(f"\n**Chi nhánh: {branch}**")
        for s in services[:5]:
            price_str = f"{s['price']:,.0f} VND" if isinstance(s['price'], (int, float)) else str(s['price'])
            context_lines.append(f"- {s['service_name_vn']} | Nhóm: {s['service_group']} | Giá: {price_str}")

    context_text = "\n".join(context_lines)
    prompt = f"Dữ liệu so sánh:\n---\n{context_text}\n---\n\nCâu hỏi: {user_query}\n\nHãy lập bảng so sánh giá giữa các chi nhánh:"

    try:
        final_answer = call_llm(prompt=prompt, system_prompt=COMPARE_PRICE_PROMPT) + DISCLAIMER_TEXT
    except Exception as e:
        logger.error(f"Compare price synthesis failed: {e}")
        final_answer = "Xin lỗi, đã xảy ra lỗi khi so sánh giá." + DISCLAIMER_TEXT
    
    step_trace = {
        "step": "compare_price",
        "input": {"normalized_query": normalized_query, "branches": list(branch_data.keys())},
        "output": {"results_count": len(results), "branches_found": list(branch_data.keys())}
    }

    logger.info("=== Compare Price Node END ===")
    return {"final_answer": final_answer, "tool_results": results, "debug_trace": debug_trace + [step_trace]}
