import sys
from loguru import logger

# Remove default handler
logger.remove()

# Add standard console handler with colors and formatting
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True
)

# Optional: Add file handler for persistence
# logger.add("logs/app.log", rotation="10 MB", level="INFO")

def get_logger():
    return logger
