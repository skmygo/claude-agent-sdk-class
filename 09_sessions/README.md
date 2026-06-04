# 09 — Session 持久化：斷點續談、分叉探索

## 觀念

`query()` 預設**無記憶**——這次問完，下次它就忘了。Session 讓對話能跨多次呼叫延續：Claude 記得讀過哪些檔、做過哪些分析、聊過什麼。

```
第一輪  query("我的幸運數字是 7")  ──► 拿到 session_id
第二輪  query("幸運數字是多少？", resume=session_id)  ──► "7"（記得！）
分叉    query(..., resume=id, fork_session=True)      ──► 從這點長出平行支線
```

## 四個關鍵選項

| 選項 | 作用 |
|------|------|
| 抓 `session_id` | 從 `SystemMessage(init)` 的 `data["session_id"]` 取得 |
| `resume="<id>"` | 接回指定 session，帶著完整上下文繼續 |
| `continue_conversation=True` | 接續「最近一次」對話，不必自己記 id |
| `fork_session=True` | 搭配 resume：從該 session 分叉出新支線，原 session 不變 |

## 核心流程

```python
# 1) 第一輪：開場訊息就帶 session_id
async for message in query(prompt="...", options=options):
    if isinstance(message, SystemMessage) and message.subtype == "init":
        session_id = message.data["session_id"]

# 2) 續談
async for message in query(prompt="...", options=ClaudeAgentOptions(resume=session_id)):
    ...
```

## resume vs fork：差在哪

```
原 session:  A ── B ── C
                       │
   resume     → 接在 C 後面繼續：A-B-C-D（同一條線，會改到原 session）
   fork       → 從 C 複製一份分出去：A-B-C-C'（原 session 停在 C 不動）
```

`fork_session` 適合「我想從這個狀態試幾種不同走法」，每條支線互不干擾。

## session 存在哪？

預設 SDK 把 session 以 **JSONL** 存在本機檔案系統（Claude Code 的 session 目錄）。所以重開程式也 `resume` 得回來。想換成 Redis / Postgres / S3 等後端，用 `session_store`（第 19 課）。

## 重要觀念

- **`session_id` 在開場那則就有**：不必等到結束，看到 `SystemMessage(init)` 立刻能抓。
- **`continue_conversation` 是「最近一次」的捷徑**：互動式 CLI 很方便，但多 session 並行時容易搞混，建議顯式 `resume`。
- **`ClaudeSDKClient` 的多輪 ≠ session 持久化**：`client` 在「同一條連線內」自然記得前文（第 10 課）；session 是把記憶**跨程序、跨次呼叫**存下來。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
