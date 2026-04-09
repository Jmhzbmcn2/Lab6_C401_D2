import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))
# (Fallback to default if not defined)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
