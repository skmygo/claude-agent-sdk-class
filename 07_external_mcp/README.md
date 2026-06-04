# 07 — 外部 MCP 伺服器：接上整個工具生態系

## 觀念

[MCP（Model Context Protocol）](https://modelcontextprotocol.io)是工具的「通用插座」。社群已經寫好[數百個 MCP 伺服器](https://github.com/modelcontextprotocol/servers)——檔案系統、瀏覽器（Playwright）、資料庫、GitHub、Slack…。你不必自己實作，掛上去就有：

```
第 05 課：自己寫工具（跑在你的行程內）
第 07 課：接別人寫好的 MCP 伺服器（跑在另一個程序）  ← 本課
```

## 三種傳輸型態

| 型態 | 設定 | 用在 |
|------|------|------|
| **stdio** | `{"command": "npx", "args": [...]}` | 本地子程序（最常見） |
| **http** | `{"type": "http", "url": "...", "headers": {...}}` | 遠端 HTTP 服務 |
| **sse** | `{"type": "sse", "url": "...", "headers": {...}}` | 遠端 SSE 服務 |

stdio 不用寫 `type`（預設就是 stdio）。

## 核心流程

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "fs": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]},
    },
    allowed_tools=["mcp__fs__list_directory", "mcp__fs__read_file"],
)
```

1. `mcp_servers` 用一個 dict 設定多個 server，key 是掛載名（這裡是 `"fs"`）
2. server 啟動後會「自我介紹」它有哪些工具
3. 工具全名 = `mcp__fs__<工具名>`，在 `allowed_tools` 放行你要用的

## 重要觀念

- **命名規則和第 05 課一樣**：`mcp__<掛載名>__<工具名>`。差別只是工具來自外部程序。
- **`mcp_servers` 進程內與外部可混用**：value 放 `create_sdk_mcp_server(...)` 物件就是進程內、放 dict 就是外部。一個 agent 可以同時掛兩種。
- **stdio server 需要對應的執行環境**：npm 套件要有 Node.js、Python 套件常用 `uvx`。
- **善用 server 自帶的安全邊界**：像 filesystem MCP 的最後一個參數限定可存取目錄，等於幫你先關了一層門（呼應第 17 課的沙箱觀念）。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
# 本課的 filesystem MCP 由 npx 即時下載，需要 Node.js；首次執行會稍慢
node --version
```

## 執行

```bash
python main.py
```
