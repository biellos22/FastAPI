from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from redis import Redis
from chat import ChatManager
import os

app = FastAPI()
redis_client = Redis(host='localhost', port=6379, db=0)
chat = ChatManager(redis_client)

# Montar a pasta de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join("static", "index.html")) as f:
        return f.read()

@app.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await chat.connect(chat_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await chat.broadcast(chat_id, data)
    except WebSocketDisconnect:
        chat.disconnect(chat_id, websocket)

@app.get("/history/{chat_id}")
async def get_chat_history(chat_id: str):
    history = chat.get_chat_history(chat_id)
    if not history:
        raise HTTPException(status_code=404, detail="Chat not found")
    return [message.decode('utf-8') for message in history]
