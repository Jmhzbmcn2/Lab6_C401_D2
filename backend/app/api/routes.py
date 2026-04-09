import time
from fastapi import APIRouter
from app.schemas.api_models import ChatRequest, ChatResponse
from app.graph.builder import graph_app
from app.utils.logger import get_logger

logger = get_logger()
router = APIRouter()

GENERIC_API_ERROR_MESSAGE = "Xin lỗi, hệ thống đang bận hoặc gặp lỗi tạm thời. Vui lòng thử lại sau ít phút."

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    logger.info(f"--- API Request START: POST /chat ---")
    logger.debug(f"Request Payload: {request.model_dump()}")
    
    start_time = time.time()
    
    # Init initial state
    initial_state = {
        "user_query": request.query,
        "normalized_query": None,
        "intent": None,
        "action_type": None,
        "is_emergency": False,
        "confidence_score": 0.0,
        "retrieved_services": [],
        "selected_services": [],
        "tool_results": [],
        "final_answer": "",
        "debug_trace": []
    }
    
    try:
        # Execute LangGraph Pipeline synchronously (our LLM app is synchronous for now)
        final_state = graph_app.invoke(initial_state)
        
        answer = final_state.get("final_answer", "")
        sources = final_state.get("tool_results", [])
        debug_trace = final_state.get("debug_trace", [])
        
        exec_time = time.time() - start_time
        logger.info(f"API Request SUCCESS in {exec_time:.2f}s")
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            debug_trace=debug_trace
        )
        
    except Exception:
        logger.exception("API Request FAILED with unexpected exception")
        exec_time = time.time() - start_time
        logger.info(f"API Request FAILED in {exec_time:.2f}s")
        
        return ChatResponse(
            answer=GENERIC_API_ERROR_MESSAGE,
            sources=[],
            debug_trace=[{"step": "system_error", "output": {"message": GENERIC_API_ERROR_MESSAGE}}]
        )
