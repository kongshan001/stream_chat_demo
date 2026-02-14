# HTTP Chunked Transfer 详解

> 基于 `examples/03_http_chunked.py` 的深入解析

## 目录

- [为什么需要 Chunked Transfer？](#为什么需要-chunked-transfer)
- [http.server 底层原理](#httpserver-底层原理)
- [代码逐行解析](#代码逐行解析)
- [完整数据流图示](#完整数据流图示)
- [运行测试](#运行测试)
- [与传统固定长度的对比](#与传统固定长度的对比)
- [关键技术点](#关键技术点)

---

## 为什么需要 Chunked Transfer？

### 传统 HTTP 响应的局限

```
HTTP/1.1 200 OK
Content-Length: 100
Content-Type: text/plain

[固定的100字节数据]
```

**问题：** 必须预先知道数据总长度，无法实现流式输出。

### Chunked Transfer 解决方案

```
HTTP/1.1 200 OK
Transfer-Encoding: chunked
Content-Type: text/plain

8\r\n
第一块数据\r\n
8\r\n
第二块数据\r\n
0\r\n
\r\n
```

**优势：** 可以边生成边发送，无需预知总长度！

---

## http.server 底层原理

### 1. 架构图

```
┌─────────────────────────────────────────────────┐
│              HTTP 客户端                         │
│           (浏览器、curl 等)                      │
└──────────────────┬──────────────────────────────┘
                   │ TCP 连接
                   │
┌──────────────────▼──────────────────────────────┐
│              HTTPServer                          │
│         1. 监听端口 8003                         │
│         2. 接受 TCP 连接                         │
│         3. 解析 HTTP 请求                        │
│         4. 调用 Handler 处理                      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│        BaseHTTPRequestHandler                    │
│                                                 │
│   ┌─────────────────────────────────────────┐  │
│   │  self.rfile  (读取请求)                  │  │
│   │    ↓                                    │  │
│   │  解析请求行 (GET / HTTP/1.1)             │  │
│   │  解析请求头                             │  │
│   │  解析请求体                             │  │
│   └─────────────────────────────────────────┘  │
│                                                 │
│   ┌─────────────────────────────────────────┐  │
│   │  self.wfile  (写入响应)                  │  │
│   │    ↓                                    │  │
│   │  发送响应行                             │  │
│   │  发送响应头                             │  │
│   │  发送响应体                             │  │
│   └─────────────────────────────────────────┘  │
│                                                 │
│   用户继承此类，重写 do_GET() 等 HTTP 方法       │
└─────────────────────────────────────────────────┘
```

### 2. 关键对象解释

#### self.rfile (请求流)

```python
# 底层实现
class SocketIO:
    def __init__(self, socket):
        self._sock = socket
    
    def readline(self):
        return self._sock.recv(...).decode()
```

#### self.wfile (响应流)

```python
# 底层实现
class SocketIO:
    def write(self, data):
        self._sock.sendall(data)
    
    def flush(self):
        # 强制立即发送，不缓冲
        pass
```

---

## 代码逐行解析

### 1. HTTP 服务器启动 (64-69行)

```python
server = HTTPServer(("0.0.0.0", 8003), ChunkedTransferHandler)
```

**HTTPServer 内部实现（简化版）：**

```python
class HTTPServer:
    def __init__(self, server_address, RequestHandlerClass):
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(server_address)
        self.socket.listen(5)
    
    def serve_forever(self):
        while True:
            # 接受新连接
            client_socket, client_address = self.socket.accept()
            
            # 为每个连接创建 Handler
            handler = self.RequestHandlerClass(
                client_socket, 
                client_address, 
                self
            )
            
            # 处理请求
            handler.handle()
```

### 2. HTTP 请求处理流程

**BaseHTTPRequestHandler.handle() 内部（伪代码）：**

```python
def handle(self):
    # 1. 读取请求行
    request_line = self.rfile.readline()
    # 解析：GET / HTTP/1.1
    
    # 2. 读取请求头
    headers = {}
    while True:
        line = self.rfile.readline()
        if line == "\r\n":
            break
        # 解析头字段
    
    # 3. 调用对应的 HTTP 方法
    if method == "GET":
        self.do_GET()
    elif method == "POST":
        self.do_POST()
```

### 3. 响应头设置 (8-15行)

```python
self.send_response(200)
```

**send_response() 内部：**

```python
def send_response(self, code):
    # 发送状态行
    self.wfile.write(f"HTTP/1.1 {code} {reason}\r\n")
    # 例如：HTTP/1.1 200 OK
```

```python
self.send_header("Transfer-Encoding", "chunked")
```

**send_header() 内部：**

```python
def send_header(self, name, value):
    # 发送头字段
    self.wfile.write(f"{name}: {value}\r\n")
```

```python
self.end_headers()
```

**end_headers() 内部：**

```python
def end_headers(self):
    # 发送空行，头结束
    self.wfile.write("\r\n")
    self.wfile.flush()
```

**此时客户端收到的完整响应头：**

```
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Cache-Control: no-cache
Transfer-Encoding: chunked

（空行，头结束）
```

### 4. Chunk 数据发送 (29-55行)

**Chunk 格式规范（RFC 7230）：**

```
[十六进制长度]\r\n
[数据内容]\r\n
```

**示例：发送 "第一块数据\n"**

```python
# 步骤1：编码为字节
data_bytes = "第一块数据\n".encode("utf-8")
# 结果：b'\xe7\xac\xac\xe4\xb8\x80\xe5\x9d\x97\xe6\x95\xb0\xe6\x8d\xae\n'

# 步骤2：计算长度
length = len(data_bytes)  # 13 字节（UTF-8编码）

# 步骤3：转为十六进制
chunk_size = hex(13)[2:]  # 'd'

# 步骤4：构造 chunk
chunk = f"d\r\n第一块数据\n\r\n"
```

**客户端收到的完整数据流：**

```
HTTP/1.1 200 OK
Transfer-Encoding: chunked
Content-Type: text/plain; charset=utf-8

d\r\n
第一块数据\n\r\n
d\r\n
第二块数据\n\r\n
d\r\n
第三块数据\n\r\n
d\r\n
第四块数据\n\r\n
e\r\n
最后一块数据\n\r\n
0\r\n
\r\n
```

### 5. 结束标记 (52-55行)

```python
self.wfile.write(b"0\r\n\r\n")
```

这告诉客户端数据流结束了。

---

## 完整数据流图示

```
客户端                      服务器 (self.wfile)
  │                            │
  │ ──────── GET / ──────────>│
  │                            │
  │<──── HTTP/1.1 200 OK ─────│
  │<──── Transfer-Encoding:   │
  │       chunked ────────────│
  │<──── (空行) ──────────────│
  │                            │
  │<───── d\r\n ──────────────│  (13的十六进制)
  │<───── 第一块数据\n\r\n ────│
  │                            │  等待 0.5s
  │<───── d\r\n ──────────────│
  │<───── 第二块数据\n\r\n ────│
  │                            │  等待 0.5s
  │<───── d\r\n ──────────────│
  │<───── 第三块数据\n\r\n ────│
  │                            │  等待 0.5s
  │<───── d\r\n ──────────────│
  │<───── 第四块数据\n\r\n ────│
  │                            │  等待 0.5s
  │<───── e\r\n ──────────────│  (14的十六进制)
  │<───── 最后一块数据\n\r\n ───│
  │                            │
  │<───── 0\r\n\r\n ──────────│  (结束标记)
  │                            │
```

---

## 运行测试

### 启动服务器

```bash
python examples/03_http_chunked.py
```

输出：
```
HTTP Chunked Transfer 演示服务启动在 http://localhost:8003
使用 curl 测试: curl -N http://localhost:8003
按 Ctrl+C 停止服务
```

### 在另一个终端测试

```bash
curl -N http://localhost:8003
```

### curl 的 -N 参数说明

```
-N, --no-buffer
  禁用 curl 的缓冲，立即显示收到的数据
```

---

## 与传统固定长度的对比

### 传统方式（需要预知长度）

```python
# 必须先计算总长度
total_length = len(data1) + len(data2) + len(data3)
self.send_header("Content-Length", str(total_length))
self.end_headers()
self.wfile.write(data1 + data2 + data3)
```

**缺点：**
- 必须预先生成所有数据
- 无法实现流式输出
- 内存占用大
- 响应时间长

### Chunked 方式（流式）

```python
self.send_header("Transfer-Encoding", "chunked")
self.end_headers()
# 边生成边发送
send_chunk(data1)
time.sleep(1)
send_chunk(data2)
time.sleep(1)
send_chunk(data3)
```

**优点：**
- 边生成边发送
- 实时流式输出
- 节省内存
- 用户体验好

---

## 关键技术点

1. **HTTP/1.1 协议**
   - Chunked Transfer 是 HTTP/1.1 的特性
   - HTTP/1.0 不支持

2. **TCP 流式传输**
   - 利用 TCP 的流式特性
   - 不需要等待完整数据

3. **wfile.flush()**
   - 强制立即发送
   - 不使用缓冲区

4. **十六进制长度**
   - Chunk 大小用十六进制表示
   - 不包含 `\r\n` 在长度中

5. **结束标记**
   - `0\r\n\r\n` 表示数据流结束
   - 必须发送，否则客户端会一直等待

---

## 扩展阅读

- [RFC 7230 - HTTP/1.1 Message Syntax and Routing](https://tools.ietf.org/html/rfc7230)
- [MDN - HTTP chunked transfer encoding](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding)
- [Python http.server 文档](https://docs.python.org/3/library/http.server.html)

---

## 总结

Chunked Transfer Encoding 是实现流式输出的核心技术：

- ✅ 不需要预先知道数据总长度
- ✅ 可以边生成边发送数据
- ✅ 提供更好的用户体验
- ✅ 节省服务器内存

掌握这个技术，你就能理解 ChatGPT 等 AI 产品是如何实现逐字输出的！
