# SSE (Server-Sent Events) 协议详解

> 基于 `examples/04_sse_protocol.py` 的深入解析

## 目录

- [什么是 SSE？](#什么是-sse)
- [为什么需要 SSE？](#为什么需要-sse)
- [SSE 与其他技术的对比](#sse-与其他技术的对比)
- [SSE 协议规范详解](#sse-协议规范详解)
- [http.server 实现 SSE 的底层原理](#httpserver-实现-sse-的底层原理)
- [代码逐行解析](#代码逐行解析)
- [完整数据流图示](#完整数据流图示)
- [前端如何使用 SSE](#前端如何使用-sse)
- [SSE 的特点和限制](#sse-的特点和限制)
- [运行测试](#运行测试)
- [实际应用场景](#实际应用场景)

---

## 什么是 SSE？

**Server-Sent Events (SSE)** 是一种服务器推送技术，允许服务器向客户端（通常是浏览器）推送实时数据。

**核心特点：**
- 基于 HTTP 协议，无需额外协议
- 单向通信：服务器 → 客户端
- 长连接：建立一次连接，持续接收数据
- 浏览器原生支持：`EventSource` API
- 自动重连：连接断开后自动尝试重连

**典型应用：**
- ChatGPT 等AI聊天界面
- 实时股票行情
- 社交媒体动态更新
- 在线协作编辑
- 实时通知推送

---

## 为什么需要 SSE？

### 传统 HTTP 请求的局限

**轮询 (Polling) 方式：**
```
客户端 ────── 请求 ──────> 服务器
         <──── 响应 ─────

(等待1秒)

客户端 ────── 请求 ──────> 服务器
         <──── 响应 ─────
```

**缺点：**
- 大量无效请求
- 延迟高（必须等待间隔）
- 服务器压力大
- 浪费带宽

### SSE 的优势

```
客户端 ──── 建立连接 ────> 服务器
         ←─ 保持长连接 ─→
         ←── 事件1 ─────
         ←── 事件2 ─────
         ←── 事件3 ─────
         (持续推送)
```

**优点：**
- ✅ 实时性强，无延迟
- ✅ 减少请求数量
- ✅ 节省带宽
- ✅ 实现简单，基于HTTP
- ✅ 浏览器原生支持

---

## SSE 与其他技术的对比

### 技术对比表

| 特性 | SSE | WebSocket | Polling | Long Polling |
|------|-----|-----------|---------|--------------|
| **通信方向** | 单向（服务器→客户端） | 双向 | 单向 | 单向 |
| **协议** | HTTP | WebSocket + HTTP | HTTP | HTTP |
| **连接方式** | 长连接 | 长连接 | 短连接 | 长连接 |
| **实时性** | 高 | 极高 | 低 | 中等 |
| **实现复杂度** | 低 | 高 | 低 | 中等 |
| **浏览器支持** | 原生 | 原生 | 原生 | 原生 |
| **自动重连** | 支持 | 需手动实现 | 不需要 | 需手动实现 |
| **服务器负载** | 低 | 中 | 高 | 中 |
| **适用场景** | 服务器推送 | 实时双向通信 | 简单轮询 | 兼容方案 |

### 什么时候选择 SSE？

**使用 SSE 的场景：**
- ❗ 只需要服务器向客户端推送数据
- ❗ 不需要客户端主动发送消息
- ❗ 需要自动重连机制
- ❗ 期望简单的实现方式

**典型场景：**
```
✅ AI聊天（ChatGPT风格）
✅ 实时新闻推送
✅ 股票/加密货币价格
✅ 社交媒体动态
✅ 系统通知
✅ 实时日志监控
```

**使用 WebSocket 的场景：**
```
✅ 聊天室（双向通信）
✅ 在线游戏
✅ 协作编辑
✅ 实时多人交互
✅ 需要低延迟的双向通信
```

---

## SSE 协议规范详解

### 1. HTTP 响应头

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no

（空行）
```

**关键字段说明：**

| 头字段 | 说明 | 必需 |
|--------|------|------|
| `Content-Type: text/event-stream` | 告知客户端这是SSE流 | ✅ 必需 |
| `Cache-Control: no-cache` | 禁止缓存，确保实时性 | ✅ 推荐 |
| `Connection: keep-alive` | 保持长连接 | ✅ 推荐 |
| `X-Accel-Buffering: no` | Nginx不缓冲（使用Nginx时） | ⚠️ 可选 |

### 2. SSE 事件格式

**基本格式：**
```
field: value\n
field: value\n
\n
```

**关键字段：**

| 字段 | 说明 | 必需 | 示例 |
|------|------|------|------|
| `event` | 事件类型 | ❌ 可选 | `event: message` |
| `data` | 事件数据 | ✅ 必需 | `data: {"text":"hello"}` |
| `id` | 事件ID | ❌ 可选 | `id: 123` |
| `retry` | 重连时间（毫秒）| ❌ 可选 | `retry: 3000` |

**重要规则：**
- 每个字段以 `field: value` 格式
- 字段后必须跟 `\n`
- 事件之间用 `\n\n` 分隔（空行）
- `data` 可以多行，每行都要加 `data:` 前缀

### 3. 完整示例

**单个事件：**
```
event: message
data: Hello World

```

**多个事件：**
```
event: connected
data: {"status": "connected"}

event: thinking
data: {"step": "正在分析"}

event: content
data: {"text": "Hello"}
data: {"text": " World"}

event: done
data: {"reason": "完成"}
retry: 3000

```

**多行 data：**
```
data: {
data:   "name": "张三",
data:   "age": 25
data: }

```

### 4. 特殊事件类型

**默认事件（没有 event 字段）：**
```
data: 这是普通消息

```
JavaScript：`evtSource.onmessage = (e) => console.log(e.data)`

**自定义事件类型：**
```
event: alert
data: 警告信息

event: update
data: {"status": "updated"}

```
JavaScript：
```javascript
evtSource.addEventListener('alert', (e) => console.log('警告:', e.data))
evtSource.addEventListener('update', (e) => console.log('更新:', e.data))
```

---

## http.server 实现 SSE 的底层原理

### 1. 完整架构图

```
┌──────────────────────────────────────────────────────┐
│                  浏览器客户端                          │
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │        EventSource (原生API)                   │ │
│  │  - 建立HTTP连接                                 │ │
│  │  - 解析SSE数据流                                │ │
│  │  - 分发事件给监听器                             │ │
│  │  - 自动重连                                     │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────┬───────────────────────────┘
                           │ HTTP长连接
                           │
┌──────────────────────────▼───────────────────────────┐
│              HTTPServer                               │
│                                                       │
│  监听 0.0.0.0:8004                                    │
│  接受连接                                             │
│  调用 SSEHandler                                      │
└──────────────────────────┬───────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────┐
│          SSEHandler (继承 BaseHTTPRequestHandler)     │
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  self.rfile (读取请求)                          │ │
│  │    ↓                                           │ │
│  │  解析 GET / HTTP/1.1                           │ │
│  │  解析请求头                                     │ │
│  └────────────────────────────────────────────────┘ │
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │  self.wfile (写入响应)                          │ │
│  │    ↓                                           │ │
│  │  1. send_response(200)                        │ │
│  │  2. send_header("Content-Type", ...)           │ │
│  │  3. send_header("Cache-Control", ...)          │ │
│  │  4. send_header("Connection", ...)             │ │
│  │  5. end_headers()                              │ │
│  │     ↓                                          │ │
│  │  6. 循环发送SSE事件                            │ │
│  │     - 构造 event: xxx\n                         │ │
│  │     - 构造 data: xxx\n                         │ │
│  │     - 发送 \n\n 分隔符                         │ │
│  │     - flush() 立即发送                         │ │
│  └────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

### 2. SSE 响应流程详解

**步骤1：建立连接**
```python
self.send_response(200)
```
发送：`HTTP/1.1 200 OK\r\n`

**步骤2：设置响应头**
```python
self.send_header("Content-Type", "text/event-stream")
self.send_header("Cache-Control", "no-cache")
self.send_header("Connection", "keep-alive")
```
发送：
```
Content-Type: text/event-stream\r\n
Cache-Control: no-cache\r\n
Connection: keep-alive\r\n
```

**步骤3：结束响应头**
```python
self.end_headers()
```
发送：`\r\n\r\n` （空行）

**步骤4：发送SSE事件**
```python
sse_message = f"event: {event_type}\ndata: {data_json}\n\n"
self.wfile.write(sse_message.encode("utf-8"))
self.wfile.flush()
```

### 3. 长连接保持机制

**服务器端：**
- 不关闭 TCP 连接
- 持续写入数据到 `wfile`
- 每次写入后调用 `flush()` 立即发送

**客户端（浏览器）：**
- 保持连接打开
- 持续读取数据流
- 解析 SSE 格式
- 触发对应的事件监听器

**连接断开处理：**
- 服务器：关闭 `wfile`，结束连接
- 客户端：自动尝试重连（默认3秒）

---

## 代码逐行解析

### 1. 导入和类定义 (1-7行)

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json


class SSEHandler(BaseHTTPRequestHandler):
    """Server-Sent Events (SSE) 协议演示"""
```

- `BaseHTTPRequestHandler`: HTTP请求处理器基类
- `HTTPServer`: HTTP服务器
- `time`: 模拟延迟
- `json`: 序列化数据

### 2. 发送响应头 (9-20行)

```python
def do_GET(self):
    self.send_response(200)

    # SSE 专用的 Content-Type
    self.send_header("Content-Type", "text/event-stream")
    self.send_header("Cache-Control", "no-cache")

    # 保持连接的重要配置
    self.send_header("Connection", "keep-alive")
    self.send_header("X-Accel-Buffering", "no")

    self.end_headers()
```

**逐行解释：**

| 行号 | 代码 | 说明 |
|------|------|------|
| 10 | `send_response(200)` | 发送HTTP 200状态 |
| 13 | `Content-Type: text/event-stream` | 关键！标识这是SSE流 |
| 14 | `Cache-Control: no-cache` | 禁止缓存 |
| 17 | `Connection: keep-alive` | 保持长连接 |
| 18 | `X-Accel-Buffering: no` | Nginx不缓冲（生产环境重要）|
| 20 | `end_headers()` | 结束响应头，发送空行 |

### 3. 定义事件数据 (26-34行)

```python
events = [
    {"event": "connected", "data": {"message": "服务器连接成功"}},
    {"event": "thinking", "data": {"step": "正在分析问题"}},
    {"event": "thinking", "data": {"step": "搜索知识库"}},
    {"event": "content", "data": {"text": "这是流式输出的一部分"}},
    {"event": "content", "data": {"text": "这是流式输出的下一部分"}},
    {"event": "done", "data": {"reason": "完成"}},
]
```

**事件类型说明：**
- `connected`: 连接建立通知
- `thinking`: AI思考过程
- `content`: 实际内容
- `done`: 完成标记

### 4. 发送SSE事件 (36-56行)

```python
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
```

**详细分解：**

**步骤1：获取事件类型**
```python
event_type = event.get("event", "message")
```
- 使用 `.get()` 防止键不存在
- 默认事件类型为 `"message"`

**步骤2：序列化数据**
```python
data_json = json.dumps(event["data"], ensure_ascii=False)
```
- 将Python字典转为JSON字符串
- `ensure_ascii=False` 保持中文不转义

**步骤3：构造SSE消息**
```python
sse_message = f"event: {event_type}\ndata: {data_json}\n\n"
```

**格式示例：**
```
event: connected
data: {"message": "服务器连接成功"}

```

**步骤4：写入响应**
```python
self.wfile.write(sse_message.encode("utf-8"))
self.wfile.flush()
```
- `encode("utf-8")`: 转为字节
- `flush()`: 强制立即发送，不缓冲

### 5. 禁用日志 (61-62行)

```python
def log_message(self, format, *args):
    pass
```

重写 `log_message` 方法，禁止打印HTTP访问日志。

### 6. 启动服务器 (65-77行)

```python
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
```

- `("0.0.0.0", 8004)`: 监听所有网络接口的8004端口
- `serve_forever()`: 持续运行，处理请求

---

## 完整数据流图示

### 服务器 → 客户端 数据流

```
时间轴    服务器发送 (self.wfile)          客户端接收
  │                                        │
  │  HTTP/1.1 200 OK                      │
  │  Content-Type: text/event-stream      │
  │  Cache-Control: no-cache              │  ← 建立SSE连接
  │  Connection: keep-alive               │
  │                                        │
  │  event: connected                     │
  │  data: {"message":"服务器连接成功"}   │  ← 触发 onconnected
  │                                        │
  │  (等待1秒)                            │
  │                                        │
  │  event: thinking                      │
  │  data: {"step":"正在分析问题"}         │  ← 触发 onthinking
  │                                        │
  │  (等待1秒)                            │
  │                                        │
  │  event: thinking                      │
  │  data: {"step":"搜索知识库"}           │  ← 触发 onthinking
  │                                        │
  │  (等待1秒)                            │
  │                                        │
  │  event: content                       │
  │  data: {"text":"这是流式输出的一部分"} │  ← 触发 oncontent
  │                                        │
  │  (等待1秒)                            │
  │                                        │
  │  event: content                       │
  │  data: {"text":"这是流式输出的下一部分"}│ ← 触发 oncontent
  │                                        │
  │  (等待1秒)                            │
  │                                        │
  │  event: done                          │
  │  data: {"reason":"完成"}              │  ← 触发 ondone
  │                                        │
  │  [连接关闭]                           │
  │                                        │  ← [自动重连]
```

### curl 测试输出

```bash
$ curl -N http://localhost:8004

event: connected
data: {"message":"服务器连接成功"}

event: thinking
data: {"step":"正在分析问题"}

event: thinking
data: {"step":"搜索知识库"}

event: content
data: {"text":"这是流式输出的一部分"}

event: content
data: {"text":"这是流式输出的下一部分"}

event: done
data: {"reason":"完成"}
```

---

## 前端如何使用 SSE

### 1. EventSource API

**基本用法：**
```javascript
// 创建EventSource对象
const evtSource = new EventSource('http://localhost:8004');

// 监听默认事件（没有event字段的事件）
evtSource.onmessage = function(event) {
    console.log('收到消息:', event.data);
    const data = JSON.parse(event.data);
    console.log('解析后的数据:', data);
};

// 监听自定义事件
evtSource.addEventListener('connected', function(event) {
    console.log('已连接:', event.data);
});

evtSource.addEventListener('thinking', function(event) {
    const data = JSON.parse(event.data);
    console.log('思考:', data.step);
});

evtSource.addEventListener('content', function(event) {
    const data = JSON.parse(event.data);
    console.log('内容:', data.text);
});

evtSource.addEventListener('done', function(event) {
    console.log('完成:', event.data);
    evtSource.close();  // 关闭连接
});

// 错误处理
evtSource.onerror = function(event) {
    console.error('SSE错误:', event);
    // 会自动重连
};

// 手动关闭连接
// evtSource.close();
```

### 2. 完整的聊天界面示例

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SSE 聊天演示</title>
</head>
<body>
    <div id="messages"></div>
    <input type="text" id="messageInput">
    <button onclick="sendMessage()">发送</button>

    <script>
        const messagesDiv = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');
        let evtSource = null;

        function sendMessage() {
            const message = messageInput.value;
            if (!message) return;

            // 显示用户消息
            addMessage('user', message);
            messageInput.value = '';

            // 创建SSE连接
            evtSource = new EventSource(`/chat/${encodeURIComponent(message)}`);

            // 监听连接成功
            evtSource.addEventListener('connected', (e) => {
                console.log('已连接');
            });

            // 监听思考过程
            evtSource.addEventListener('thinking', (e) => {
                const data = JSON.parse(e.data);
                updateThinking(data.step);
            });

            // 监听内容
            evtSource.addEventListener('content', (e) => {
                const data = JSON.parse(e.data);
                appendContent(data.text);
            });

            // 监听完成
            evtSource.addEventListener('done', (e) => {
                evtSource.close();
            });

            // 错误处理
            evtSource.onerror = () => {
                console.error('连接错误');
            };
        }

        function addMessage(type, text) {
            const div = document.createElement('div');
            div.className = `message ${type}`;
            div.textContent = text;
            messagesDiv.appendChild(div);
        }

        function updateThinking(step) {
            // 更新思考状态
            console.log('思考:', step);
        }

        function appendContent(text) {
            // 追加内容
            const lastMessage = messagesDiv.lastElementChild;
            if (lastMessage && lastMessage.className.includes('assistant')) {
                lastMessage.textContent += text;
            } else {
                addMessage('assistant', text);
            }
        }
    </script>
</body>
</html>
```

### 3. EventSource 属性和方法

**属性：**
```javascript
evtSource.url          // 连接的URL
evtSource.readyState   // 连接状态: 0=连接中, 1=已打开, 2=已关闭
evtSource.withCredentials  // 是否发送凭证
```

**方法：**
```javascript
evtSource.close()      // 关闭连接
```

**事件监听器：**
```javascript
evtSource.onmessage    // 默认消息事件
evtSource.onopen       // 连接打开
evtSource.onerror      // 错误事件
evtSource.addEventListener('event-name', handler)  // 自定义事件
```

---

## SSE 的特点和限制

### 优点

| 特性 | 说明 |
|------|------|
| **简单易用** | 基于HTTP，无需额外协议 |
| **浏览器原生支持** | EventSource API，无需第三方库 |
| **自动重连** | 断线自动重连，可靠性高 |
| **文本友好** | 支持UTF-8，天然支持中文 |
| **服务器推送** | 单向推送，适合大多数场景 |
| **低开销** | 比WebSocket简单，资源占用少 |

### 限制

| 限制 | 说明 | 解决方案 |
|------|------|----------|
| **单向通信** | 只能服务器→客户端 | 需要双向时使用WebSocket |
| **仅文本** | 只能传输文本数据 | 使用Base64传输二进制 |
| **同源策略** | 遵守CORS策略 | 服务器配置CORS头 |
| **连接数限制** | 每个域名最多6个连接 | 使用多个域名 |
| **浏览器兼容** | IE不支持 | 使用polyfill |

### 性能考虑

**服务器端：**
```python
# ✅ 好的做法
self.send_header("Cache-Control", "no-cache")
self.send_header("Connection", "keep-alive")
self.wfile.flush()  # 每次写入后flush

# ❌ 避免的做法
time.sleep(60)  # 不要保持空闲连接太久
# 不flush会导致缓冲延迟
```

**客户端：**
```javascript
// ✅ 好的做法
evtSource.addEventListener('done', () => {
    evtSource.close();  // 用完即关
});

// ❌ 避免的做法
// 不要创建过多EventSource
// 注意内存泄漏
```

---

## 运行测试

### 1. 启动服务器

```bash
python examples/04_sse_protocol.py
```

输出：
```
SSE 协议演示服务启动在 http://localhost:8004
使用 curl 测试: curl -N http://localhost:8004
使用 JavaScript 测试:
const evtSource = new EventSource('http://localhost:8004');
evtSource.onmessage = function(e) {
    console.log('收到消息:', e.data);
};
按 Ctrl+C 停止服务
```

### 2. 使用 curl 测试

```bash
curl -N http://localhost:8004
```

参数说明：
- `-N, --no-buffer`: 禁用缓冲，实时输出

### 3. 使用浏览器测试

**创建 test.html：**
```html
<!DOCTYPE html>
<html>
<head>
    <title>SSE 测试</title>
</head>
<body>
    <h1>SSE 测试</h1>
    <div id="output"></div>
    <script>
        const output = document.getElementById('output');
        const evtSource = new EventSource('http://localhost:8004');

        evtSource.addEventListener('connected', (e) => {
            output.innerHTML += `<p>✅ 已连接: ${e.data}</p>`;
        });

        evtSource.addEventListener('thinking', (e) => {
            const data = JSON.parse(e.data);
            output.innerHTML += `<p>💭 思考: ${data.step}</p>`;
        });

        evtSource.addEventListener('content', (e) => {
            const data = JSON.parse(e.data);
            output.innerHTML += `<p>📝 内容: ${data.text}</p>`;
        });

        evtSource.addEventListener('done', (e) => {
            output.innerHTML += `<p>🎉 完成: ${e.data}</p>`;
            evtSource.close();
        });

        evtSource.onerror = (e) => {
            output.innerHTML += `<p>❌ 错误</p>`;
        };
    </script>
</body>
</html>
```

在浏览器中打开 `test.html`，即可看到实时更新。

### 4. 使用开发者工具查看SSE

1. 打开浏览器开发者工具 (F12)
2. 切换到 **Network** 标签
3. 访问测试页面
4. 找到 `event-stream` 类型的请求
5. 点击查看详细的实时数据流

---

## 实际应用场景

### 1. ChatGPT 风格的AI聊天

**后端 (Python/FastAPI)：**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def generate_response(user_message):
    yield f"event: connected\ndata: {{'status':'connected'}}\n\n"

    # 模拟思考
    for step in ["分析问题", "搜索知识", "构建回答"]:
        yield f"event: thinking\ndata: {{'step':'{step}'}}\n\n"
        await asyncio.sleep(1)

    # 模拟逐字输出
    response = f"回答: {user_message}"
    for char in response:
        yield f"event: content\ndata: {{'text':'{char}'}}\n\n"
        await asyncio.sleep(0.1)

    yield f"event: done\ndata: {{'reason':'complete'}}\n\n"

@app.get("/chat/{message}")
async def chat(message: str):
    return StreamingResponse(
        generate_response(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

**前端：**
```javascript
const evtSource = new EventSource(`/chat/${encodeURIComponent(message)}`);

evtSource.addEventListener('thinking', (e) => {
    showThinking(JSON.parse(e.data).step);
});

evtSource.addEventListener('content', (e) => {
    appendText(JSON.parse(e.data).text);
});

evtSource.addEventListener('done', () => {
    evtSource.close();
});
```

### 2. 实时股票行情

```python
async def stock_ticker():
    import random
    while True:
        price = round(random.uniform(100, 200), 2)
        yield f"event: price\ndata: {{'symbol':'AAPL','price':{price}}}\n\n"
        await asyncio.sleep(1)
```

### 3. 实时日志监控

```python
async def log_stream():
    with open('app.log') as f:
        for line in tail(f):
            yield f"event: log\ndata: {{'line':'{line.strip()}'}}\n\n"
            await asyncio.sleep(0.1)
```

---

## 总结

### SSE 核心要点

1. **协议简单** - 基于HTTP，`Content-Type: text/event-stream`
2. **格式规范** - `event: type\ndata: json\n\n`
3. **长连接** - 保持TCP连接，持续推送
4. **自动重连** - 断线自动重连，可靠性高
5. **浏览器支持** - 原生EventSource API
6. **适用场景** - 服务器推送，AI聊天，实时数据

### 最佳实践

✅ **推荐做法：**
- 设置 `Cache-Control: no-cache`
- 每次写入后调用 `flush()`
- 使用JSON格式传输数据
- 合理定义事件类型
- 及时关闭不需要的连接

❌ **避免做法：**
- 不要在SSE中传输大文件
- 不要忽略错误处理
- 不要保持空闲连接太久
- 不要忘记设置响应头

---

## 扩展阅读

- [MDN - Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [W3C SSE 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

---

掌握 SSE，你就能像 ChatGPT 一样实现流畅的实时推送体验！
