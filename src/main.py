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


@app.websocket("/tts_audio_control")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)

    audio_player.websocket = websocket
    audio_player.loop = asyncio.get_event_loop()

    try:
        while True:
            try:
                data = await websocket.receive_json()
                command = data.get("control_type")
                file_path = data.get("tts_file", "").strip()

                if command == "play":
                    success = audio_player.play(file_path)
                    if success:
                        await websocket.send_json({"status": "success"})
                    else:
                        await websocket.send_json({
                            "status":
                            "error",
                            "message":
                            "Failed to play audio"
                        })

                elif command == "stop":
                    success = audio_player.stop()
                    if success:
                        await websocket.send_json({"status": "success"})
                    else:
                        await websocket.send_json({
                            "status":
                            "error",
                            "message":
                            "Failed to stop audio"
                        })

                elif command == "pause":
                    success = audio_player.pause()
                    if success:
                        await websocket.send_json({"status": "success"})
                    else:
                        await websocket.send_json({
                            "status":
                            "error",
                            "message":
                            "Failed to pause audio"
                        })

                elif command == "resume":
                    success = audio_player.unpause()
                    if success:
                        await websocket.send_json({"status": "success"})
                    else:
                        await websocket.send_json({
                            "status":
                            "error",
                            "message":
                            "Failed to resume audio"
                        })
                else:
                    await websocket.send_json(
                        {"error": f"Invalid command：{command}"})
            except Exception as e:
                await websocket.send_json({"error": str(e)})
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        websocket_clients.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
