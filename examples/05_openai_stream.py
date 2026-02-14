import os
from openai import OpenAI


def stream_chat_completion():
    """OpenAI 流式聊天完成示例"""

    # 初始化客户端
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

    print("=" * 60)
    print("OpenAI 流式输出示例")
    print("=" * 60)

    # 创建流式请求
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手"},
            {"role": "user", "content": "请用Python解释什么是生成器，给出简单例子"},
        ],
        stream=True,
    )

    print("\nAI回答:")
    print("-" * 60)

    # 逐个处理流式响应
    for chunk in stream:
        # 获取内容
        content = chunk.choices[0].delta.content

        # 打印实时输出
        if content:
            print(content, end="", flush=True)

    print("\n" + "-" * 60)
    print("输出完成")


def stream_with_thinking():
    """带思考过程的流式输出"""

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

    print("\n" + "=" * 60)
    print("带思考过程的流式输出")
    print("=" * 60)

    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "解释一下什么是递归"}],
        stream=True,
        temperature=0.7,
    )

    full_content = ""

    print("\n实时流式输出:")
    print("-" * 60)

    for chunk in stream:
        content = chunk.choices[0].delta.content

        if content:
            full_content += content
            print(content, end="", flush=True)

    print("\n" + "-" * 60)
    print(f"总字符数: {len(full_content)}")


def simulate_stream_without_api():
    """模拟流式输出（不需要API密钥）"""

    print("=" * 60)
    print("模拟AI流式输出（无需API密钥）")
    print("=" * 60)

    # 预设的回答
    response = (
        "生成器（Generator）是Python中一种特殊的迭代器，它可以暂停和恢复函数的执行状态。\n\n"
        "关键特点：\n"
        "1. 使用 yield 关键字\n"
        "2. 延迟计算，节省内存\n"
        "3. 可以表示无限序列\n\n"
        "简单示例：\n"
        "def my_generator():\n"
        "    yield 1\n"
        "    yield 2\n"
        "    yield 3\n\n"
        "for value in my_generator():\n"
        "    print(value)\n\n"
        "输出：1, 2, 3"
    )

    print("\n模拟流式输出:")
    print("-" * 60)

    for char in response:
        print(char, end="", flush=True)
        # 模拟网络延迟
        import time

        time.sleep(0.01)

    print("\n" + "-" * 60)
    print("模拟完成")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        # 使用模拟模式（不需要API密钥）
        simulate_stream_without_api()
    elif len(sys.argv) > 1 and sys.argv[1] == "--thinking":
        # 带思考过程
        stream_with_thinking()
    else:
        # 标准示例
        print("\n提示：")
        print("  python 05_openai_stream.py         # 需要OPENAI_API_KEY")
        print("  python 05_openai_stream.py --simulate  # 模拟模式（无需API密钥）")
        print("  python 05_openai_stream.py --thinking  # 带思考过程")
        print()

        try:
            choice = input("选择模式 [1:需要API / 2:模拟模式] (默认2): ").strip()
        except EOFError:
            choice = "2"

        if choice == "1":
            stream_chat_completion()
        else:
            simulate_stream_without_api()
