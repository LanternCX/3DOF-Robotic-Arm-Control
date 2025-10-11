import serial
import atexit
from typing import Optional
from utils.logger import get_logger

logger = get_logger("Serials")

class SerialInstance:
    """
    封装单个串口实例，支持链式调用
    """
    def __init__(self, ser: serial.Serial, name: str):
        self._ser = ser
        self.name = name

    def send(self, msg: str) -> "SerialInstance":
        try:
            self._ser.write(msg.encode("utf-8"))
            logger.debug(f"[SerialInstance] {self.name} sent: {msg}")
        except Exception as e:
            logger.error(f"[SerialInstance] {self.name} failed to send: {e}")
        return self  # 支持链式调用

    def close(self) -> "SerialInstance":
        try:
            if self._ser.is_open:
                self._ser.close()
                logger.info(f"[SerialInstance] Closed {self.name}")
        except Exception as e:
            logger.error(f"[SerialInstance] Failed to close {self.name}: {e}")
        return self  # 支持链式调用


class Serials:
    _instances: dict[str, SerialInstance] = {}

    @classmethod
    def register(cls, port: str, name: str, baudrate: int = 115200, timeout: float = 1) -> Optional[SerialInstance]:
        if name in cls._instances:
            logger.warning(f"[Serials] {name} already registered.")
            return cls._instances[name]

        try:
            ser = serial.Serial(port, baudrate, timeout=timeout)
            instance = SerialInstance(ser, name)
            cls._instances[name] = instance
            logger.info(f"[Serials] Registered {name} on {port}")
            return instance
        except Exception as e:
            logger.error(f"[Serials] Failed to open {port} for {name}: {e}")
            return None

    @classmethod
    def get(cls, name: str) -> Optional[SerialInstance]:
        return cls._instances.get(name, None)

    @classmethod
    def send(cls, name: str, msg: str) -> Optional[SerialInstance]:
        instance = cls.get(name)
        if instance is None:
            logger.error(f"[Serials] No serial registered with name {name}")
            return None
        return instance.send(msg)

    @classmethod
    def close_all(cls):
        for name, instance in cls._instances.items():
            instance.close()
        cls._instances.clear()


atexit.register(Serials.close_all)
