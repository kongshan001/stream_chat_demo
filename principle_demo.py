from http.server import BaseHTTPRequestHandler, HTTPServer
import io


class DebugHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

        output = io.StringIO()

        output.write("=" * 60 + "\n")
        output.write("HTTP 流式响应底层原理\n")
        output.write("=" * 60 + "\n\n")

        output.write("1. 传统响应模式\n")
        output.write("   - 服务器生成完整内容\n")
        output.write("   - Content-Length 必须已知\n")
        output.write("   - 客户端等待完整接收\n\n")

        output.write("2. 流式响应模式\n")
        output.write("   - 服务器边生成边发送\n")
        output.write("   - Content-Length 未知\n")
        output.write("   - 使用 Transfer-Encoding: chunked\n\n")

        output.write("3. Chunked 编码格式\n")
        output.write("   每个数据块格式：\n")
        output.write("   [十六进制字节长度]\\r\\n[数据内容]\\r\\n\n")
        output.write("   结束标记：\n")
        output.write("   0\\r\\n\\r\\n\n\n")

        output.write("4. 示例数据块\n")
        data = "Hello"
        output.write(f"   数据: '{data}'\n")
        output.write(f"   字节长度: {len(data.encode())}\n")
        output.write(f"   十六进制: {hex(len(data.encode()))[2:]}\n")
        output.write(f"   完整chunk: {hex(len(data.encode()))[2:]}\\r\\n{data}\\r\\n\n")

        output.write("=" * 60 + "\n")

        self.wfile.write(output.getvalue().encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8002), DebugHandler)
    print("原理说明服务启动在 http://localhost:8002")
    server.serve_forever()
