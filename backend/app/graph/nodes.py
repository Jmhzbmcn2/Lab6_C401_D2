import json
import re
from app.graph.state import AgentState
from app.utils.logger import get_logger
from pydantic import BaseModel, Field
from app.services.llm_service import call_llm, call_llm_structured
from app.database.chroma_db import search_services
from app.database.sqlite_db import query_services_by_ids, fallback_fuzzy_search

logger = get_logger()

class IntentSchema(BaseModel):
    normalized_query: str = Field(description="Chỉ giữ lại tên dịch vụ lõi (vd: siêu âm thai, xét nghiệm máu), loại bỏ các từ hỏi giá, địa điểm.")
    intent_branch: str = Field(description="Chỉ điền 'Times City' hoặc 'Smart City'. Nếu không rõ thì để ''.")

def query_understanding_node(state: AgentState) -> dict:
    logger.info("=== Query Understanding Node START ===")
    user_query = state.get("user_query", "")
    logger.debug(f"Input User Query: {user_query}")
    
    debug_trace = state.get("debug_trace", [])
    
    system_prompt = (
        "Bạn là một chuyên gia trích xuất thông tin. Nhiệm vụ của bạn là lấy ra Tên Dịch Vụ thuần túy và tên Chi Nhánh từ câu hỏi."
    )
    
    try:
        # Sử dụng structured generate_content
        raw_json = call_llm_structured(prompt=user_query, schema_class=IntentSchema, system_prompt=system_prompt)
        
        parsed = json.loads(raw_json)
        normalized_query = parsed.get("normalized_query", user_query)
        intent = parsed.get("intent_branch", "")
            
        logger.debug(f"Normalized Query: {normalized_query} | Intent: {intent}")
        
    except Exception as e:
        logger.error(f"Query understanding failed: {e}")
        normalized_query = user_query
        intent = ""

    step_trace = {
        "step": "query_understanding",
        "input": {"user_query": user_query},
        "output": {"normalized_query": normalized_query, "intent": intent}
    }
    
    logger.info("=== Query Understanding Node END ===")
    return {"normalized_query": normalized_query, "intent": intent, "debug_trace": debug_trace + [step_trace]}


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
        # we do not raise to allow graceful fallback
        
    step_trace = {
        "step": "retrieval",
        "input": {"queries": queries, "intent": intent},
        "output": {"retrieved_count": len(all_retrieved), "retrieved_ids": [r["id"] for r in all_retrieved]}
    }
    
    logger.info("=== Retrieval Node END ===")
    return {"retrieved_services": all_retrieved, "debug_trace": state["debug_trace"] + [step_trace]}


def tool_execution_node(state: AgentState) -> dict:
    logger.info("=== Tool Execution Node START ===")
    retrieved = state.get("retrieved_services", [])
    intent = state.get("intent", "")
    normalized_query = state.get("normalized_query", "")
    
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
        "output": {"tool_results_count": len(tool_results), "tool_results": tool_results}
    }
    
    logger.info("=== Tool Execution Node END ===")
    return {"tool_results": tool_results, "debug_trace": state["debug_trace"] + [step_trace]}


def llm_synthesis_node(state: AgentState) -> dict:
    logger.info("=== LLM Synthesis Node START ===")
    tool_results = state.get("tool_results", [])
    user_query = state.get("user_query", "")
    
    if not tool_results:
        # Should usually go to fallback, but just in case
        return fallback_node(state)
        
    # Tạo text tổng hợp
    context_lines = []
    for r in tool_results:
        price_str = f"{r['price']:,.0f} VND" if isinstance(r['price'], (int, float)) else str(r['price'])
        context_lines.append(f"- Chi nhánh: {r['branch']} | Dịch vụ: {r['service_name_vn']} | Nhóm: {r['service_group']} | Giá tiền: {price_str}")
        
    context_text = "\n".join(context_lines)
    
    system_prompt = (
        "Bạn là một trợ lý tư vấn y tế của Bệnh viện Vinmec.\n"
        "Nhiệm vụ của bạn là dựa vào Thông Tin Được Cho dưới đây để trả lời câu hỏi của người dùng.\n"
        "Luôn trả lời lịch sự, format đẹp mắt bằng Markdown. Nếu danh sách quá dài, hãy liệt kê tối đa top 5-7 dịch vụ sát nhất.\n"
        "Không bịa ra thông tin. Trả lời trực tiếp vào giá tiền."
    )
    
    prompt = f"Thông Tin Được Cho (Từ Cơ Sở Dữ Liệu):\n---\n{context_text}\n---\n\nCâu hỏi người dùng: {user_query}\nTrợ lý trả lời:"
    
    logger.debug(f"Calling LLM with {len(tool_results)} context items")
    try:
        final_answer = call_llm(prompt=prompt, system_prompt=system_prompt)
        logger.debug(f"LLM Synthesis succeeded. Output length: {len(final_answer)}")
    except Exception as e:
        logger.error(f"LLM Synthesis failed: {e}")
        final_answer = "Xin lỗi, đã xảy ra lỗi trong quá trình tổng hợp kết quả (LLM Error)."
        
    step_trace = {
        "step": "llm_synthesis",
        "input": {"context_items": len(tool_results)},
        "output": {"answer_length": len(final_answer)}
    }
    
    logger.info("=== LLM Synthesis Node END ===")
    return {"final_answer": final_answer, "debug_trace": state["debug_trace"] + [step_trace]}


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
    
    return {"final_answer": final_answer, "debug_trace": state["debug_trace"] + [step_trace]}
