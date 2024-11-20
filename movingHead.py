import asyncio
from websocket import create_connection, WebSocketException
import time, random

class MovingHead():
    def __init__(self) -> None:
        self.ws = create_connection("ws://127.0.0.1:9999/qlcplusWS")
        for i in range(21):
            self.send_message(i, 0)

    def send_message(self, channel, value):
        try:
            message = f"CH|{channel}|{value}"
            self.ws.send(message)
            print(f"Sent: {message}")
        except WebSocketException as e:
            print(f"WebSocket Handshake: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    