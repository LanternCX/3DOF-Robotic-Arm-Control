from loguru import logger
import sys
import inspect

logger.remove()
logger.add(
    sys.stdout,
    format=(
        "<green>{time:HH:mm:ss}</green> "
        "| <cyan>{extra[module]}</cyan> "
        "| <yellow>{extra[name]}</yellow> "
        "| <level>{level}</level> "
        "| {message}"
    ),
    level="INFO",
)

def get_logger(name: str):
    # 获取调用者模块名（例如 control.move）
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    module_name = module.__name__ if module else "unknown"

    # 绑定模块名和自定义名称
    return logger.bind(module=module_name, name=name)
