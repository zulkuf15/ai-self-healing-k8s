from loguru import logger
import sys
from config import Config

logger.remove()
logger.add(sys.stdout, level=Config.LOG_LEVEL, colorize=True,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
