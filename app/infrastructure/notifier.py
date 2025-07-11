from typing import List

from fastapi import WebSocket


class PostNotifier:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.usernames: dict = {}  # websocket -> username

    async def connect(self, websocket: WebSocket, username: str = ""):
        await websocket.accept()
        self.active_connections.append(websocket)
        if username:
            self.usernames[websocket] = username

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.usernames:
            del self.usernames[websocket]

    async def broadcast_new_post(self, poster_username: str):
        # Notify all except the poster
        for ws in list(self.active_connections):
            try:
                if self.usernames.get(ws) != poster_username:
                    await ws.send_json({"event": "new_post"})
            except Exception:
                self.disconnect(ws)


post_notifier = PostNotifier()
