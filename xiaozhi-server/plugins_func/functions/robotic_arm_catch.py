import json

from plugins_func.register import register_function, ToolType, ActionResponse, Action
from config.logger import setup_logging
from utils.client import client

TAG = __name__
logger = setup_logging()

catch_function_desc = {
  "type": "function",
  "function": {
    "name": "robotic_arm_catch",
    "description": "控制机械臂抓取特定类型的物体（如 green、yellow、blue、yolo）",
    "parameters": {
      "type": "object",
      "properties": {
        "catch_type": {
          "type": "string",
          "enum": ["green", "blue", "yellow", "yolo"],
          "description": "要抓取的物体类型，可选值为 green、blue、yellow 或 yolo"
        }
      },
      "required": ["catch_type"]
    }
  }
}


@register_function(
    "robotic_arm_catch", catch_function_desc, ToolType.IOT_CTL
)
async def robotic_arm_catch(conn, catch_type: str):
    try:
        # 参数合法性校验
        if catch_type not in ("green", "blue", "yolo", "yellow"):
            raise ValueError("type 参数必须为 'green'、'blue' 或 'yolo'")

        # 打印日志
        logger.bind(tag=TAG).info(f"Catch target type: {catch_type}")

        # 构造命令
        cmd = {
            "cmd": "catch",
            "args": [catch_type]
        }

        # 发送命令
        await client.send(json.dumps(cmd))
        data = await client.receive()

        if data:
            res = json.loads(data)
            logger.info(f"receive: {res}")

            success = res.get("success", True)
            msg = res.get("msg", "抓取完成")

            if success:
                return ActionResponse(
                    action=Action.RESPONSE,
                    result="Catch Success",
                    response=f"机械臂已成功抓取 {catch_type} 类型目标。"
                )
            else:
                return ActionResponse(
                    action=Action.RESPONSE,
                    result="Catch Failed",
                    response=f"机械臂抓取失败：{msg}"
                )
        else:
            raise Exception("Serial Timeout")

    except Exception as e:
        logger.bind(tag=TAG).error(f"处理抓取任务时出错: {e}")
        return ActionResponse(
            action=Action.NONE,
            result="Catch Failed",
            response=str(e)
        )
