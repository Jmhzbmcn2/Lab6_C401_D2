import json
import re
from app.graph.state import AgentState
from app.utils.logger import get_logger
from pydantic import BaseModel, Field
from app.services.llm.llm_service import call_llm, call_llm_structured
from app.database.chroma_db import search_services
from app.database.sqlite_db import query_services_by_ids, fallback_fuzzy_search, compare_services_across_branches

logger = get_logger()

# === EMERGENCY KEYWORDS ===
EMERGENCY_KEYWORDS = [
    "cấp cứu", "ngất", "ngất xỉu", "bất tỉnh", "co giật", "khó thở",
    "không thở được", "chảy máu nhiều", "xuất huyết", "tai nạn",
    "đột quỵ", "nhồi máu", "ngừng tim", "hôn mê", "sốc phản vệ",
    "ngộ độc", "uống thuốc tự tử", "tự tử", "chấn thương nặng",
    "gãy xương", "bỏng nặng", "điện giật", "đuối nước",
    "emergency", "unconscious", "seizure", "stroke",
]

EMERGENCY_RESPONSE = """
## 🚨 PHÁT HIỆN TÌNH HUỐNG KHẨN CẤP

**Hãy GỌI NGAY số cấp cứu:**

# ☎️ 115

Hoặc liên hệ cấp cứu Vinmec:
- **Vinmec Times City:** 024 3974 3556
- **Vinmec Smart City:** 024 7300 0115 (Ext: 115)

> ⚠️ Tôi là trợ lý AI tra cứu giá dịch vụ, **KHÔNG có khả năng hỗ trợ y tế khẩn cấp**. Vui lòng liên hệ bác sĩ hoặc đội cấp cứu ngay lập tức.
"""

DISCLAIMER_TEXT = "\n\n---\n*⚠️ Thông tin mang tính THAM KHẢO. Giá có thể thay đổi tùy thời điểm và điều kiện bảo hiểm. Để được tư vấn chính xác nhất, vui lòng liên hệ hotline Vinmec.*"

# === SCHEMAS ===
class IntentSchema(BaseModel):
    normalized_query: str = Field(description="Chỉ giữ lại tên dịch vụ lõi (vd: siêu âm thai, xét nghiệm máu), loại bỏ các từ hỏi giá, địa điểm.")
    intent_branch: str = Field(description="Chỉ điền 'Times City' hoặc 'Smart City'. Nếu không rõ thì để ''.")
    action_type: str = Field(description="Phân loại: 'compare_price' nếu người dùng muốn SO SÁNH giá giữa các chi nhánh/bệnh viện, 'triage' nếu hỏi giá hoặc tư vấn dịch vụ cụ thể, 'general' nếu là câu hỏi chung.")


# === NODE 1: EMERGENCY CHECK ===
def emergency_check_node(state: AgentState) -> dict:
    logger.info("=== Emergency Check Node START ===")
    user_query = state.get("user_query", "").lower()
    debug_trace = state.get("debug_trace", [])
    
    is_emergency = False
    matched_keywords = []
    
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in user_query:
            is_emergency = True
            matched_keywords.append(keyword)
    
    step_trace = {
        "step": "emergency_check",
        "input": {"user_query": user_query},
        "output": {"is_emergency": is_emergency, "matched_keywords": matched_keywords}
    }
    
    result = {
        "is_emergency": is_emergency,
        "debug_trace": debug_trace + [step_trace]
    }
    
    if is_emergency:
        logger.warning(f"🚨 EMERGENCY DETECTED. Keywords: {matched_keywords}")
        result["final_answer"] = EMERGENCY_RESPONSE
    
    logger.info("=== Emergency Check Node END ===")
    return result


# === NODE 2: QUERY UNDERSTANDING ===
def query_understanding_node(state: AgentState) -> dict:
    logger.info("=== Query Understanding Node START ===")
    user_query = state.get("user_query", "")
    logger.debug(f"Input User Query: {user_query}")
    
    debug_trace = state.get("debug_trace", [])
    
    system_prompt = (
        "Bạn là một chuyên gia trích xuất thông tin y tế. Nhiệm vụ của bạn là:\n"
        "1. Lấy ra Tên Dịch Vụ thuần túy từ câu hỏi.\n"
        "2. Xác định Chi Nhánh (Times City hoặc Smart City) nếu có.\n"
        "3. Phân loại action_type: 'compare_price' nếu người dùng muốn so sánh giá giữa các nơi/chi nhánh, 'triage' nếu hỏi giá cụ thể hoặc tư vấn, 'general' nếu là câu hỏi chung."
    )
    
    try:
        raw_json = call_llm_structured(prompt=user_query, schema_class=IntentSchema, system_prompt=system_prompt)
        
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


# === NODE 3: COMPARE PRICE ===
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
    
    system_prompt = (
        "Bạn là trợ lý tư vấn giá dịch vụ y tế của Bệnh viện Vinmec.\n"
        "Nhiệm vụ: Dựa vào dữ liệu bên dưới, lập BẢNG SO SÁNH GIÁ giữa các chi nhánh.\n"
        "Format bằng Markdown table rõ ràng. Chỉ dùng dữ liệu được cung cấp, KHÔNG bịa.\n"
        "Luôn kết thúc bằng ghi chú: thông tin tham khảo."
    )
    
    prompt = f"Dữ liệu so sánh:\n---\n{context_text}\n---\n\nCâu hỏi: {user_query}\n\nHãy lập bảng so sánh giá giữa các chi nhánh:"

    try:
        final_answer = call_llm(prompt=prompt, system_prompt=system_prompt) + DISCLAIMER_TEXT
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


# === NODE 4: RETRIEVAL (Existing, enhanced with confidence) ===
def retrieval_node(state: AgentState) -> dict:
    logger.info("=== Retrieval Node START ===")
    query = state.get("normalized_query", state["user_query"])
    intent = state.get("intent", "")
    logger.debug(f"Query: {query} | Intent: {intent}")
    
    queries = [q.strip() for q in query.split(',')] if ',' in query else [query]
    all_retrieved = []
    
    try:
        for q in queries:
            if not q: continue
            results = search_services(query=q, n_results=10, branch=intent)
            all_retrieved.extend(results)
            logger.debug(f"Retrieved {len(results)} services for '{q}'")
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        
    step_trace = {
        "step": "retrieval",
        "input": {"queries": queries, "intent": intent},
        "output": {"retrieved_count": len(all_retrieved), "retrieved_ids": [r["id"] for r in all_retrieved]}
    }
    
    logger.info("=== Retrieval Node END ===")
    return {"retrieved_services": all_retrieved, "debug_trace": state["debug_trace"] + [step_trace]}


# === NODE 5: TOOL EXECUTION (Enhanced with Confidence Scoring) ===
def tool_execution_node(state: AgentState) -> dict:
    logger.info("=== Tool Execution Node START ===")
    retrieved = state.get("retrieved_services", [])
    intent = state.get("intent", "")
    normalized_query = state.get("normalized_query", "")
    
    # Compute composite confidence score
    if retrieved:
        distances = [r.get('distance', 1.0) for r in retrieved[:5]]
        avg_distance = sum(distances) / len(distances)
        # Convert distance to similarity (lower distance = higher confidence)
        vector_similarity = max(0, 1 - avg_distance)
        
        # Symptom match: how many of the top results have low distance
        good_matches = sum(1 for d in distances if d < 0.4)
        symptom_match_score = good_matches / len(distances)
        
        # Intent clarity: if we have a clear branch intent
        intent_clarity_score = 1.0 if intent else 0.5
        
        confidence_score = round(
            0.5 * vector_similarity + 
            0.3 * symptom_match_score + 
            0.2 * intent_clarity_score, 
            3
        )
    else:
        confidence_score = 0.0

    logger.debug(f"Confidence Score: {confidence_score}")
    
    # Filter out items with very bad distance (> 0.6)
    valid_retrieved = [r for r in retrieved if r.get('distance', 0) < 0.6]
    
    result_ids = list(set([r["id"] for r in valid_retrieved]))
    logger.debug(f"Input IDs to query SQLite after thresholding: {len(result_ids)}")
    
    tool_results = []
    try:
        if result_ids:
            tool_results = query_services_by_ids(result_ids, branch_filter=intent)
            logger.debug(f"SQLite returned {len(tool_results)} exact tool matches from Chroma")
            
        # Fallback keyword search if chroma returned nothing or threshold blocked it
        if not tool_results:
            logger.warning("No valid results from ChromaDB. Engaging SQLite Fuzzy Fallback.")
            tool_results = fallback_fuzzy_search(normalized_query, branch_filter=intent)
            logger.debug(f"Fuzzy fallback returned {len(tool_results)} exact tool matches")
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        
    step_trace = {
        "step": "tool_execution",
        "input": {"ids_count": len(result_ids), "intent": intent, "chroma_valid": len(valid_retrieved)},
        "output": {
            "tool_results_count": len(tool_results), 
            "confidence_score": confidence_score,
            "tool_results": tool_results
        }
    }
    
    logger.info("=== Tool Execution Node END ===")
    return {
        "tool_results": tool_results, 
        "confidence_score": confidence_score,
        "debug_trace": state["debug_trace"] + [step_trace]
    }


# === NODE 6: LLM SYNTHESIS (Enhanced with Disclaimer + Phrasing Control) ===
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
    
    system_prompt = (
        "Bạn là một trợ lý tư vấn giá dịch vụ y tế của Bệnh viện Vinmec.\n"
        "NGUYÊN TẮC BẮT BUỘC:\n"
        "1. CHỈ dùng dữ liệu được cung cấp. TUYỆT ĐỐI KHÔNG bịa ra thông tin hoặc giá tiền.\n"
        "2. Luôn dùng cụm từ 'Thông tin tham khảo' hoặc 'Gợi ý' thay vì 'chẩn đoán' hay 'kết luận'.\n"
        "3. KHÔNG đưa ra lời khuyên y khoa, chẩn đoán bệnh hay kê đơn thuốc.\n"
        "4. Trả lời lịch sự, format đẹp mắt bằng Markdown. Nếu danh sách quá dài, liệt kê top 5-7 dịch vụ phù hợp nhất.\n"
        "5. Trả lời trực tiếp vào giá tiền và tên dịch vụ."
    )
    
    prompt = f"Thông Tin Được Cho (Từ Cơ Sở Dữ Liệu):\n---\n{context_text}\n---\n\nCâu hỏi người dùng: {user_query}\nTrợ lý trả lời:"
    
    logger.debug(f"Calling LLM with {len(tool_results)} context items. Confidence: {confidence_score}")
    try:
        final_answer = call_llm(prompt=prompt, system_prompt=system_prompt)
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
    return {"final_answer": final_answer, "debug_trace": state["debug_trace"] + [step_trace]}


# === NODE 7: CLARIFICATION (When confidence is too low) ===
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
    return {"final_answer": final_answer, "debug_trace": state["debug_trace"] + [step_trace]}


# === NODE 8: FALLBACK ===
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
    
    return {"final_answer": final_answer, "debug_trace": state["debug_trace"] + [step_trace]}
