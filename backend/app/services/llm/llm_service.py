from google import genai
from google.genai import types
from app.core.config import GEMINI_API_KEY
from app.utils.logger import get_logger

logger = get_logger()

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to intialize genai client: {e}")

def call_llm(prompt: str, system_prompt: str = "") -> str:
    """Gọi Google Gemini API (gemini-2.5-flash-lite)."""
    if not client:
        logger.error("GEMINI_API_KEY is not set or client init failed!")
        return "[Lỗi hệ thống]: Không tìm thấy GEMINI_API_KEY."
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
            ),
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"[Lỗi kết nối Gemini]: {e}"

def call_llm_structured(prompt: str, schema_class, system_prompt: str = "") -> str:
    """Gọi Google Gemini API và bắt buộc trả về chuỗi JSON theo schema Pydantic."""
    if not client:
        logger.error("GEMINI_API_KEY is not set or client init failed!")
        return "{}"
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=schema_class
            ),
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini Structured API error: {e}")
        return "{}"
