# 使用 FastAPI 创建 WebSocket 服务器
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket 连接处理
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 这里替换为你的程序输出
            dialogue_message = {
                "playerId": 1,
                "content": "这是一条新消息",
                "time": "Day 1"
            }
            await websocket.send_json(dialogue_message)
            await asyncio.sleep(2)  # 每2秒发送一条消息
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

# 或者使用 HTTP API
@app.get("/api/dialogue")
async def get_dialogue():
    # 这里返回你的程序输出
    return [
        {
            "playerId": 1,
            "content": "这是第一条消息",
            "time": "Day 1"
        },
        {
            "playerId": 2,
            "content": "这是第二条消息",
            "time": "Day 1"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)