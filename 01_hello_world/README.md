# 01 — Hello World：最小可運行範例

## 觀念

整個 Claude Agent SDK 最基礎的形狀就三步：

```
你的 prompt ──► query() ──► 一串訊息（async 迭代）──► 你挑出想要的
```

`query()` 不是「問一句答一句」那麼單純。它背後是一個 **agent 迴圈**：Claude 可能會讀檔、跑指令、跑好幾輪，最後才結束。這些過程會以一連串「訊息」吐給你，你用 `async for` 逐則接收。

這一課的任務（`2 + 2`）不需要工具，所以訊息很少；但形狀和複雜任務完全一樣。

## 核心流程

1. `ClaudeAgentOptions(...)` — 準備設定（可省略）
2. `async for message in query(prompt=..., options=...)` — 送出並逐則接收訊息
3. `isinstance(message, AssistantMessage)` — 認出 Claude 的發言
4. 走訪 `message.content`，挑出 `TextBlock` 拿文字
5. `isinstance(message, ResultMessage)` — 任務結束，可拿成本/回合數

## 重要觀念

- **回傳的是「訊息流」不是字串**：別期待 `query()` 直接給你一句答案，它給的是一串訊息，文字藏在 `AssistantMessage.content` 的 `TextBlock` 裡。
- **`AssistantMessage.content` 是一個 list**：一則發言可能同時有「說話」(`TextBlock`) 和「要用工具」(`ToolUseBlock`)，所以要走訪。
- **`ResultMessage` 一定在最後**：想知道花了多少錢、跑了幾輪，看它。`total_cost_usd` 在沒有計費時可能是 `0`/`None`，記得防呆。
- **`async` 是必須的**：SDK 全程非同步，入口要用 `asyncio.run(...)`（也可換成 `anyio`）。

## 前置需求

```bash
pip install claude-agent-sdk      # 需 Python 3.10+、Node.js
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
