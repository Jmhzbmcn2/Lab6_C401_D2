from openai import OpenAI
from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.utils.logger import get_logger

logger = get_logger()

GENERIC_SYSTEM_ERROR_MESSAGE = (
    "Xin lỗi, hệ thống đang gặp sự cố tạm thời. Vui lòng thử lại sau ít phút."
)

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    logger.error("OPENAI_API_KEY is not set.")

def call_llm(prompt: str, system_prompt: str = "") -> str:
    """Gọi OpenAI ChatCompletion API."""
    if not client:
        logger.error("OPENAI_API_KEY is not set or client init failed!")
        return GENERIC_SYSTEM_ERROR_MESSAGE

    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.1,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return GENERIC_SYSTEM_ERROR_MESSAGE

def call_llm_structured(prompt: str, schema_class, system_prompt: str = "") -> str:
    """Gọi OpenAI ChatCompletion API và yêu cầu trả về JSON theo schema Pydantic."""
    if not client:
        logger.error("OPENAI_API_KEY is not set or client init failed!")
        return "{}"

    try:
        schema_text = schema_class.model_json_schema()
        schema_text = str(schema_text)
    except Exception:
        schema_text = str(getattr(schema_class, '__name__', schema_class))

    structured_prompt = (
        f"{prompt}\n\n"
        "Vui lòng chỉ trả về JSON hợp lệ khớp với schema sau, không thêm chú thích nào khác:\n"
        f"{schema_text}"
    )

    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": structured_prompt})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.1,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI Structured API error: {e}")
        return "{}"
