def basic_generator():
    """基础生成器示例 - 演示yield关键字"""
    print("开始执行生成器")
    yield "第一块数据"
    yield "第二块数据"
    yield "第三块数据"
    print("生成器执行完毕")


def infinite_stream():
    """无限流生成器 - 模拟持续输出"""
    count = 0
    while True:
        yield f"消息 {count}\n"
        count += 1


def process_data_stream():
    """数据处理流 - 演示流式处理数据"""
    data = ["用户输入", "进行分词", "转换为向量", "查询知识库", "生成回答"]

    for step in data:
        yield f"正在处理: {step}\n"
        yield f"{step} 完成\n"


from time import sleep


def simulate_ai_response():
    """模拟AI流式响应 - 最接近实际使用场景"""
    response = "这是一个模拟的AI回答，我会一个字一个字地输出给你。"

    for char in response:
        yield char


if __name__ == "__main__":
    print("=" * 50)
    print("1. 基础生成器示例")
    print("=" * 50)
    gen = basic_generator()
    print(f"生成器对象: {gen}")
    print(f"生成器类型: {type(gen)}")

    print("\n逐个获取数据:")
    for item in gen:
        print(f"  收到: {item}")

    print("\n" + "=" * 50)
    print("2. 限制无限流的前5条")
    print("=" * 50)
    count = 0
    for item in infinite_stream():
        print(item.strip())
        count += 1
        if count >= 5:
            break

    print("\n" + "=" * 50)
    print("3. 数据处理流")
    print("=" * 50)
    for item in process_data_stream():
        print(item.strip())

    print("\n" + "=" * 50)
    print("4. 模拟AI流式响应")
    print("=" * 50)
    for char in simulate_ai_response():
        print(char, end="", flush=True)
    print()
