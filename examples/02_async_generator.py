import asyncio


async def async_basic():
    """基础异步生成器"""
    print("开始异步生成器")

    for i in range(3):
        await asyncio.sleep(0.5)
        yield f"异步数据 {i}\n"


async def async_simulate_thinking():
    """模拟AI思考过程"""
    thinking_steps = [
        "理解问题...",
        "搜索知识库...",
        "分析上下文...",
        "构建回答...",
        "生成内容...",
    ]

    for step in thinking_steps:
        yield step
        await asyncio.sleep(0.3)


async def async_word_stream(text):
    """将文本逐词流式输出"""
    words = text.split()

    for word in words:
        yield word + " "
        await asyncio.sleep(0.1)


async def consume_async_generator(generator):
    """消费异步生成器的示例"""
    async for item in generator:
        print(item, end="", flush=True)


async def main():
    print("=" * 50)
    print("1. 基础异步生成器")
    print("=" * 50)
    await consume_async_generator(async_basic())

    print("\n" + "=" * 50)
    print("2. 模拟AI思考过程")
    print("=" * 50)
    async for step in async_simulate_thinking():
        print(f"  {step}")
        await asyncio.sleep(0.2)

    print("\n" + "=" * 50)
    print("3. 逐词流式输出")
    print("=" * 50)
    text = "AI流式输出让对话更加自然流畅"
    await consume_async_generator(async_word_stream(text))
    print()


if __name__ == "__main__":
    asyncio.run(main())
