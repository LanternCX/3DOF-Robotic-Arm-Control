import asyncio
from command.controller import handle_server_message
from utils.socket import WebSocketClient, WebSocketServer


async def test():
    server = WebSocketServer(host="localhost", port=8765, on_message=handle_server_message)
    await server.start()

if __name__ == "__main__":
    asyncio.run(test())