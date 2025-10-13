import inspect
import json
from utils.logger import get_logger

logger = get_logger("registry")

# 命令注册表： cmd_name -> handler
COMMAND_REGISTRY = {}

def command(cmd_name: str):
    """
    命令注册装饰器，用于注册处理函数
    """
    def decorator(func):
        if cmd_name in COMMAND_REGISTRY:
            logger.warning(f"Command '{cmd_name}' already registered, overwriting.")
        COMMAND_REGISTRY[cmd_name] = func
        logger.info(f"Registered command: {cmd_name} -> {func.__name__}")
        return func
    return decorator


