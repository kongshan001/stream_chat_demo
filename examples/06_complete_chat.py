from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json


app = FastAPI()

# 允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_chat_response(message: str):
    """生成聊天响应 - SSE格式"""

    # 发送开始事件
    yield f"event: start\ndata: {json.dumps({'message': '连接成功'})}\n\n"

    # 模拟思考过程
    thinking_steps = [
        "正在理解你的问题...",
        "分析上下文信息...",
        "搜索相关知识...",
        "构建回答内容...",
    ]

    for step in thinking_steps:
        yield f"event: thinking\ndata: {json.dumps({'step': step})}\n\n"
        await asyncio.sleep(0.5)

    # 模拟AI逐字输出
    response = f"你说的是：{message}。这是一个完整的AI聊天演示，支持流式输出！"

    for char in response:
        yield f"event: content\ndata: {json.dumps({'text': char})}\n\n"
        await asyncio.sleep(0.03)

    # 发送完成事件
    yield f"event: done\ndata: {json.dumps({'reason': '完成'})}\n\n"


async def generate_plain_stream():
    """生成普通文本流"""

    messages = [
        "这是一个完整的AI聊天演示！\n",
        "支持以下功能：\n",
        "1. Server-Sent Events (SSE) 协议\n",
        "2. 流式逐字输出\n",
        "3. 思考过程可视化\n",
        "4. 完整的聊天界面\n\n",
        "你可以尝试发送任意消息！\n",
    ]

    for msg in messages:
        for char in msg:
            yield char
            await asyncio.sleep(0.02)


@app.get("/")
async def home():
    """首页 - 演示流式输出"""
    return StreamingResponse(
        generate_plain_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/chat/{message}")
async def chat(message: str):
    """聊天接口 - SSE格式"""
    return StreamingResponse(
        generate_chat_response(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.post("/chat")
async def chat_post(message: dict):
    """POST聊天接口"""
    user_message = message.get("message", "")
    return StreamingResponse(
        generate_chat_response(user_message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("完整AI聊天应用")
    print("=" * 60)
    print("\n启动服务...")
    print("API端点:")
    print("  GET  http://localhost:8000/")
    print("  GET  http://localhost:8000/chat/{message}")
    print("  POST http://localhost:8000/chat")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
