from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class IntentSchema(BaseModel):
    normalized_query: str = Field(description="Chỉ giữ lại tên dịch vụ lõi (vd: siêu âm thai, xét nghiệm máu), loại bỏ các từ hỏi giá, địa điểm.")
    intent_branch: str = Field(description="Chỉ điền 'Times City' hoặc 'Smart City'. Nếu không rõ thì để ''.")

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    debug_trace: List[Dict[str, Any]]
