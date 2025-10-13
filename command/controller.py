import importlib
import pkgutil
import json
import command.handler  # 命令包
from utils.logger import get_logger
from .registry import COMMAND_REGISTRY

logger = get_logger("controller")

# 自动导入 controller.handler 下的所有模块
for loader, name, is_pkg in pkgutil.iter_modules(command.handler.__path__):
    importlib.import_module(f"command.handler.{name}")

async def handle_server_message(data, websocket):
    """
    服务端收到客户端消息时调用
    """
    logger.info(f"Received from client: {data}")

    cmd = data.get("cmd")
    args = data.get("args", [])

    if not cmd:
        await websocket.send(json.dumps({"type": "error", "msg": "Missing command"}))
        return

    # 调用命令调度器
    await dispatch_command(cmd, args, websocket)


async def dispatch_command(cmd: str, args: list, websocket):
    handler = COMMAND_REGISTRY.get(cmd)
    if not handler:
        await websocket.send(json.dumps({"type": "error", "msg": f"Unknown command: {cmd}"}))
        return

    try:
        # 传入 websocket + args
        await handler(websocket, *args)
    except Exception as e:
        await websocket.send(json.dumps({"type": "error", "msg": f"Execution error: {str(e)}"}))
