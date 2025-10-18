from utils.socket import WebSocketClient
import asyncio

async def socket_init():
    client = WebSocketClient()
    await client.connect()

if __name__ == "__main__":
    asyncio.run(socket_init())
