import json

from plugins_func.register import register_function, ToolType, ActionResponse, Action
from config.logger import setup_logging
from utils.client import client

TAG = __name__
logger = setup_logging()

robotic_arm_control_function_desc = {
  "type": "function",
  "function": {
    "name": "robotic_arm_position",
    "description": "进行机械臂的正运动学(fk)或逆运动学(ik)计算",
    "parameters": {
      "type": "object",
      "properties": {
        "mode": {
          "type": "string",
          "enum": ["ik", "fk"],
          "description": "ik 表示逆运动学解算，fk 表示正运动学解算"
        },
        "params": {
          "type": "array",
          "items": {
            "type": "number"
          },
          "minItems": 3,
          "maxItems": 3,
          "description": "ik 模式下填入柱面坐标 [r, theta, h]；fk 模式下填入机械臂三个关节（底座、肩关节、肘关节）角度 [theta1, theta2, theta3]"
        }
      },
      "required": ["mode", "params"]
    }
  }
}

@register_function(
    "robotic_arm_position", robotic_arm_control_function_desc, ToolType.IOT_CTL
)
async def robotic_arm_position(conn, mode: str, params: list[float]):
    try:
        # 确保 params 长度为3
        if len(params) != 3:
            raise ValueError("参数长度错误，必须为3个")

        # 解析模式
        if mode not in ("ik", "fk"):
            raise ValueError("mode 参数必须为 'ik' 或 'fk'")

        x, y, z = params

        # 打印日志
        logger.bind(tag=TAG).info(
            f"Kinematics Mod: {mode}, args: x={x}, y={y}, z={z}"
        )

        cmd = {
            "cmd": f"{mode}",
            "args": [f"{x}", f"{y}", f"{z}"]
        }

        await client.send(json.dumps(cmd))
        data = await client.receive()

        if data:
            res = json.loads(data).get("args", [])
            logger.info(f"receive: {res}")
            if mode == "ik":
                return ActionResponse(
                    action=Action.RESPONSE,
                    result="IK Success",
                    response=f"运动学逆解完成，底座为{res[0]:.2f}度 肩关节为{res[1]:.2f}度 肘关节为{res[2]:.2f}度"
                )
            elif mode == "fk":
                return ActionResponse(
                    action=Action.RESPONSE,
                    result="FK Success",
                    response=f"运动学正解完成，柱面坐标下半径为 {res[0]:.2f}毫米 旋转角为{res[1]:.2f}度 高度为{res[2]:.2f}毫米"
                )
            else:
                raise Exception("Invalid mode")
        else:
            raise Exception("Serial Timeout")


    except Exception as e:
        logger.bind(tag=TAG).error(f"处理运动学解析错误: {e}")
        return ActionResponse(
            action=Action.NONE,
            result="FK or Ik Failed",
            response=str(e)
        )
