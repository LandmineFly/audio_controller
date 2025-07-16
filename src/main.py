from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from controller import AudioPlayer

import uvicorn
import asyncio
import json
import re

app = FastAPI()

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_player = AudioPlayer()
#存储 WebSocket 连接
websocket_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_json()
                command = data.get("command")
                file_path = data.get("file_path")

                if command == "play":
                    audio_player.enqueue(file_path)
                elif command == "stop":
                    audio_player.stop(file_path)
                elif command == "audio_progress":
                    audio_player.audio_progress()
                else
                    await websocket.send_json({"error": f"Invalid command：{command}"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    finally:
        websocket_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

            
