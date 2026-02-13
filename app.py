from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


async def generate_stream():
    messages = [
        "你好！这是一个流式返回的示例。\n",
        "正在处理你的请求...\n",
        "数据加载中...\n",
        "分析完成...\n",
        "结果已生成！\n",
        "感谢使用！\n",
    ]

    for msg in messages:
        yield msg
        await asyncio.sleep(0.5)


@app.get("/")
async def stream_response():
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
