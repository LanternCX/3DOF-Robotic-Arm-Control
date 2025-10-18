from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}", level="INFO")

def get_logger(name: str):
    return logger.bind(name=name)
