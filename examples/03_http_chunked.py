from http.server import BaseHTTPRequestHandler, HTTPServer
import time


class ChunkedTransferHandler(BaseHTTPRequestHandler):
    """HTTP Chunked Transfer Encoding 演示"""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")

        # 关键：使用 Transfer-Encoding: chunked
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        print("\n" + "=" * 60)
        print("开始发送 Chunked 数据流")
        print("=" * 60)

        messages = [
            "第一块数据\n",
            "第二块数据\n",
            "第三块数据\n",
            "第四块数据\n",
            "最后一块数据\n",
        ]

        for i, msg in enumerate(messages, 1):
            # 1. 将数据编码为字节
            data_bytes = msg.encode("utf-8")

            # 2. 计算字节长度并转为十六进制
            chunk_size = hex(len(data_bytes))[2:]

            # 3. 构造 chunk: [十六进制长度]\r\n[数据]\r\n
            chunk = f"{chunk_size}\r\n{msg}\r\n"

            # 4. 打印调试信息
            print(f"Chunk {i}:")
            print(f"  原始数据: {repr(msg)}")
            print(f"  字节长度: {len(data_bytes)}")
            print(f"  十六进制长度: {chunk_size}")
            print(f"  完整chunk: {repr(chunk)}")

            # 5. 写入响应
            self.wfile.write(chunk.encode())
            self.wfile.flush()

            time.sleep(0.5)

        # 6. 发送结束标记: 0\r\n\r\n
        print("\n发送结束标记: 0\\r\\n\\r\\n")
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

        print("数据流发送完成")
        print("=" * 60 + "\n")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8003), ChunkedTransferHandler)
    print("HTTP Chunked Transfer 演示服务启动在 http://localhost:8003")
    print("使用 curl 测试: curl -N http://localhost:8003")
    print("按 Ctrl+C 停止服务")
    server.serve_forever()
