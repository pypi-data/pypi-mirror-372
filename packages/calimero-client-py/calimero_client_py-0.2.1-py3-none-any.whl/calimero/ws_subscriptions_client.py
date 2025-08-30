import asyncio
import json
from typing import Any, Callable, List, Optional
import websockets
from .types import (
    WebSocketMessage,
    SubscribeRequest,
    UnsubscribeRequest,
    SubscriptionUpdate,
    WebSocketApiResponse,
    ErrorResponse,
)


class WsSubscriptionsClient:
    def __init__(self, base_url: str, endpoint: str = "/ws"):
        self.base_url = base_url.rstrip("/")
        self.endpoint = endpoint
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.callbacks: List[Callable[[Any], None]] = []
        self.subscribed_apps: List[str] = []
        self._running = False

    async def connect(self):
        # Don't create a new connection if already connected
        if self.ws and self._running:
            return

        ws_url = (
            f"ws://{self.base_url.lstrip('http://').lstrip('https://')}{self.endpoint}"
        )
        self.ws = await websockets.connect(ws_url)
        self._running = True
        asyncio.create_task(self._listen())

    async def disconnect(self):
        self._running = False
        if self.ws:
            await self.ws.close()
            self.ws = None

    async def _listen(self):
        if not self.ws:
            raise RuntimeError("WebSocket connection not established")

        while self._running:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                for callback in self.callbacks:
                    callback(data)
            except websockets.exceptions.ConnectionClosed:
                if self._running:
                    try:
                        await self.connect()
                    except Exception as e:
                        print(f"Failed to reconnect: {e}")
                        self._running = False
                        break
            except Exception as e:
                print(f"Error in WebSocket listener: {e}")
                self._running = False
                break

    def subscribe(self, request: SubscribeRequest):
        if not self.ws:
            raise RuntimeError("WebSocket connection not established")

        self.subscribed_apps.extend(request.application_ids)
        message = WebSocketMessage(
            type="subscribe", data={"applicationIds": request.application_ids}
        )
        asyncio.create_task(self.ws.send(json.dumps(message.model_dump())))

    def unsubscribe(self, request: UnsubscribeRequest):
        if not self.ws:
            raise RuntimeError("WebSocket connection not established")

        self.subscribed_apps = [
            app_id
            for app_id in self.subscribed_apps
            if app_id not in request.application_ids
        ]
        message = WebSocketMessage(
            type="unsubscribe", data={"applicationIds": request.application_ids}
        )
        asyncio.create_task(self.ws.send(json.dumps(message.model_dump())))

    def add_callback(self, callback: Callable[[Any], None]):
        self.callbacks.append(callback)

    def remove_callback(self, callback: Callable[[Any], None]):
        self.callbacks.remove(callback)
