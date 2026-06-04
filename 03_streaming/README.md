# 03 — 即時串流：逐 token 顯示

## 觀念

預設 `query()` 會等 Claude「整段想完」才丟一則完整的 `AssistantMessage` 給你——回答長的時候，使用者只能空等。

打開 `include_partial_messages=True`，SDK 會**額外**吐出一串 `StreamEvent`，裡面是模型邊生成邊送的增量片段。即時印出來，就是打字機效果：

```
include_partial_messages=False ：   [等待…………] → "一整段答案"
include_partial_messages=True  ：   "一" "整" "段" "答" "案"  （邊生成邊到）
```

## 核心流程

1. `ClaudeAgentOptions(include_partial_messages=True)`
2. 迭代訊息，遇到 `StreamEvent` 就解析增量
3. `StreamEvent.event` 是 Anthropic 串流協定的原始 dict，從中挑出 `text_delta`
4. `print(chunk, end="", flush=True)` 即時輸出

## 怎麼從 StreamEvent 取出文字

`StreamEvent.event` 是原始事件，文字增量長這樣：

```python
{"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Py"}}
```

所以解析就是兩層判斷（見 `main.py` 的 `text_delta()`）：

```python
if event.get("type") == "content_block_delta":
    delta = event.get("delta", {})
    if delta.get("type") == "text_delta":
        return delta.get("text", "")
```

## 重要觀念

- **StreamEvent 是「額外」的，不是「取代」**：開了之後，你仍會收到完整的 `AssistantMessage` 和 `ResultMessage`。串流只是讓你「提早」看到文字。
- **event 裡不只有文字**：還有 `message_start`、`content_block_start`、`message_delta`（含 stop_reason）等。做工具進度條時可以解析更多種 delta。
- **記得 `flush=True`**：否則終端機會緩衝，看不到逐字效果。
- **這課用 `query()` 就夠**：串流不必動用 `ClaudeSDKClient`；不過互動式 App 常把兩者搭配（見第 10 課）。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
