from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json


class SSEHandler(BaseHTTPRequestHandler):
    """Server-Sent Events (SSE) 协议演示"""

    def do_GET(self):
        self.send_response(200)

        # SSE 专用的 Content-Type
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")

        # 保持连接的重要配置
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")

        self.end_headers()

        print("\n" + "=" * 60)
        print("开始发送 SSE 事件流")
        print("=" * 60)

        # 模拟多个事件
        events = [
            {"event": "connected", "data": {"message": "服务器连接成功"}},
            {"event": "thinking", "data": {"step": "正在分析问题"}},
            {"event": "thinking", "data": {"step": "搜索知识库"}},
            {"event": "content", "data": {"text": "这是流式输出的一部分"}},
            {"event": "content", "data": {"text": "这是流式输出的下一部分"}},
            {"event": "done", "data": {"reason": "完成"}},
        ]

        for i, event in enumerate(events, 1):
            # SSE 事件格式:
            # event: 事件类型 (可选)
            # data: 数据内容 (必需)
            # 空行表示事件结束

            event_type = event.get("event", "message")
            data_json = json.dumps(event["data"], ensure_ascii=False)

            # 构建 SSE 消息
            sse_message = f"event: {event_type}\ndata: {data_json}\n\n"

            print(f"事件 {i}:")
            print(f"  类型: {event_type}")
            print(f"  数据: {data_json}")
            print(f"  SSE格式:\n{repr(sse_message)}")

            self.wfile.write(sse_message.encode("utf-8"))
            self.wfile.flush()

            time.sleep(1)

        print("\nSSE 事件流发送完成")
        print("=" * 60 + "\n")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8004), SSEHandler)
    print("SSE 协议演示服务启动在 http://localhost:8004")
    print("使用 curl 测试: curl -N http://localhost:8004")
    print("使用 JavaScript 测试:")
    print("""
    const evtSource = new EventSource('http://localhost:8004');
    evtSource.onmessage = function(e) {
        console.log('收到消息:', e.data);
    };
    """)
    print("按 Ctrl+C 停止服务")
    server.serve_forever()
