from http.server import BaseHTTPRequestHandler, HTTPServer
import time


class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        messages = [
            "你好！这是原生 Python 标准库的流式返回示例。\n",
            "底层原理：HTTP 分块传输编码（Chunked Transfer Encoding）\n",
            "每个 chunk 格式：[十六进制长度]\\r\\n[数据]\\r\\n\n",
            "正在演示...\n",
            "消息 1\n",
            "消息 2\n",
            "消息 3\n",
            "流式传输完成！\n",
        ]

        for msg in messages:
            chunk_size = hex(len(msg.encode()))[2:]
            chunk = f"{chunk_size}\r\n{msg}\r\n"
            self.wfile.write(chunk.encode())
            self.wfile.flush()
            time.sleep(0.5)

        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8001), StreamHandler)
    print("原生 Python 标准库流式服务启动在 http://localhost:8001")
    print("按 Ctrl+C 停止服务")
    server.serve_forever()
