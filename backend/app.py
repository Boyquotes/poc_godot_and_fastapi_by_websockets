import os
from typing import Dict, Hashable, Iterable, Optional

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

app = FastAPI()

template_path = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_path)


origins = [
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[Hashable, WebSocket] = dict()

    async def connect(self, _id: Hashable, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[_id] = websocket

    def disconnect(self, _id: Hashable) -> None:
        self.active_connections.pop(_id)

    async def send_personal_message(self, _id: Hashable, message: str) -> None:
        await self.active_connections[_id].send_text(message)

    async def broadcast(
        self, message: str, excluded_hashes: Optional[Iterable[Hashable]] = None
    ) -> None:
        for key, connection in self.active_connections.items():
            if key in (excluded_hashes or ()):
                continue

            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int) -> None:
    await manager.connect(_id=client_id, websocket=websocket)
    await manager.broadcast(message=f"Client {client_id}: joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(
                _id=client_id, message=f"You wrote: {data}"
            )
            await manager.broadcast(
                message=f"Client #{client_id} says: {data}",
                excluded_hashes=(client_id,),
            )
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(message=f"Client #{client_id} left the chat")
