# 05 — 自訂工具：把 Python 函式變成 Claude 的工具

## 觀念

內建工具（Read / Bash / Grep…）讓 agent 能操作你的電腦。但要讓它查你的資料庫、call 你公司的 API，就得寫**自訂工具**。

Claude Agent SDK 的自訂工具，本質上是一個「進程內 MCP 伺服器」——聽起來很重，其實就兩個裝飾器與一個打包函式，整段跑在你的 Python 行程裡，沒有額外程序、沒有網路往返：

```
@tool 標記函式 ──► create_sdk_mcp_server 打包 ──► mcp_servers 掛上去
```

## 定義工具的三步

1. **定義**：用 `@tool(名稱, 說明, 參數schema)` 裝飾一個 `async` 函式
   ```python
   @tool("add", "把兩個數字相加", {"a": float, "b": float})
   async def add(args: dict) -> dict:
       return {"content": [{"type": "text", "text": f"{args['a']+args['b']}"}]}
   ```
2. **打包**：`create_sdk_mcp_server(name="toolbox", tools=[...])`
3. **掛載**：`ClaudeAgentOptions(mcp_servers={"toolbox": server}, allowed_tools=[...])`

## 兩個容易踩的點

- **工具全名 = `mcp__<伺服器名>__<工具名>`**
  伺服器掛載名是 `"toolbox"`、工具叫 `"add"`，那全名就是 `mcp__toolbox__add`。`allowed_tools` 要寫**全名**才放行得了。
- **回傳格式固定**
  一定要回 `{"content": [{"type": "text", "text": "..."}]}`。出錯時加 `"is_error": True`：
  ```python
  return {"content": [{"type": "text", "text": "除數不能為 0"}], "is_error": True}
  ```

## 參數 schema 的兩種寫法

| 寫法 | 範例 | 適合 |
|------|------|------|
| 簡寫 dict | `{"a": float, "b": float}` | 參數少、快速 |
| TypedDict / 完整 JSON Schema | 自訂類別或 dict | 需要描述、巢狀、驗證 |

## 進程內 MCP vs 外部 MCP

| | 進程內（本課） | 外部（第 07 課） |
|---|---|---|
| 怎麼來 | `@tool` + `create_sdk_mcp_server` | 別人寫好的 MCP server |
| 在哪跑 | 你的 Python 行程內 | 另一個程序（stdio / http） |
| 適合 | 你自己的商業邏輯 | 接生態系（瀏覽器、DB、雲服務…） |

## 重要觀念

- **說明（description）就是給模型的提示**：寫清楚工具「做什麼、何時用」，Claude 才挑得準。
- **工具是 async**：裡面可以 `await` 你的 DB／HTTP 呼叫。
- **這課用 `ClaudeSDKClient`**：MCP 工具搭配多輪互動最自然；用 `query()` 一樣可掛 `mcp_servers`。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
