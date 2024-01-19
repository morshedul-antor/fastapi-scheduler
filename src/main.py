from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.background import BackgroundTasks
from datetime import datetime

import asyncio
import uvicorn
import pytz

app = FastAPI()


background_task_running = False


async def background_task(websocket: WebSocket, background_tasks: BackgroundTasks):
    timezone = pytz.timezone("Asia/Dhaka")
    cancel_task = False

    while not cancel_task:
        try:
            now = datetime.now(timezone).time()
            now_str = now.strftime('%H:%M')

            # Set trigger times
            trigger_times = ['21:10', '21:13', '21:20']

            if now_str in trigger_times:
                try:
                    await websocket.send_text("API Triggered!")
                    print("Triggering API...")

                except Exception as e:
                    print(f"Error sending message: {e}")

            await asyncio.sleep(60)

        except WebSocketDisconnect:
            break


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global background_task_running

    await websocket.accept()

    # Start the background task only if it's not already running
    if not background_task_running:
        background_tasks = BackgroundTasks()
        task = asyncio.create_task(
            background_task(websocket, background_tasks))
        background_task_running = True

        try:
            while True:
                message = await websocket.receive_text()
                print(f"Received message: {message}")

        except asyncio.CancelledError:
            print("WebSocket connection closed!")

        except WebSocketDisconnect as e:
            print(f"WebSocket disconnected!")

        finally:
            task.cancel()
            background_task_running = False


@app.get("/")
def root():
    return {"message": "FastAPI Scheduler"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000,
                reload=True, log_level="info")
