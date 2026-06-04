# 19 — 進階持久化與壓縮：管好 agent 的長期記憶

## 觀念

這是收尾課，處理「長時間運作的 agent」最後兩個硬問題：

```
問題 1：對話太長，上下文要被壓縮了，重要的事會不會被壓掉？
        → PreCompact hook，在壓縮前注入「保護清單」

問題 2：session 預設存本機 JSONL，多機部署 / 查詢 / 備援怎麼辦？
        → session_store，換成你要的後端
```

第 09 課教的是「怎麼存、怎麼續」；這課教的是「**存到哪、壓縮時保住什麼**」。

## 第一招：PreCompact hook

當對話逼近上下文上限，SDK 會自動「壓縮」——把舊歷史濃縮成摘要騰出空間。問題是：濃縮時可能把你在乎的細節丟了。`PreCompact` 讓你在壓縮**前**插話：

```python
async def protect_on_compact(input_data, tool_use_id, context):
    return {"hookSpecificOutput": {
        "hookEventName": "PreCompact",
        "additionalContext": "壓縮時務必保留：需求清單、關鍵決定、待辦事項。",
    }}

hooks={"PreCompact": [HookMatcher(hooks=[protect_on_compact])]}
```

- `input_data["trigger"]`：`"auto"`（SDK 自動觸發）或 `"manual"`（使用者下 `/compact`）。
- 短對話不會觸發——只有長到需要壓縮時才進這個 hook。

## 第二招：自訂 session_store

預設後端把 session 寫成本機 JSONL。要換後端，實作 `SessionStore` 介面、傳給 `session_store`：

```python
from claude_agent_sdk import InMemorySessionStore
options = ClaudeAgentOptions(session_store=InMemorySessionStore())
```

`SessionStore` 的核心方法：

| 方法 | 作用 |
|------|------|
| `append(key, entries)` | 寫入新的對話紀錄 |
| `load(key)` | 載入某 session 的完整紀錄 |
| `list_sessions(project_key)` | 列出有哪些 session |
| `delete(key)` | 刪除 session |

| 後端 | 來源 | 適合 |
|------|------|------|
| 預設 JSONL | SDK 內建 | 單機、本地開發 |
| `InMemorySessionStore` | SDK 內建（本課用） | 測試、不需持久化 |
| Redis / Postgres / S3 | 官方 `examples/session_stores` 參考實作 | 生產、多機、要查詢/備援 |

> 自己寫 adapter 時，可用 SDK 附的 `run_session_store_conformance` 驗證是否符合介面契約。

## 重要觀念

- **壓縮是「自動省記憶體」，PreCompact 是你的發言權**：別等到資訊被壓掉才後悔，主動宣告「這些不能動」。
- **`InMemorySessionStore` 不跨程序**：程式結束記憶就沒了，只適合測試。要 `resume`（第 09 課）跨程序生效，得用會落地的後端。
- **這課把整個系列串起來**：hooks（06）＋ session（09）＋ 限制（16）＋ 記憶（18），到這裡組成一個「能長期穩定運作」的 agent。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

本課對話很短，不會觸發 `PreCompact`；它示範的是「掛法」。真正的壓縮攔截要在長對話中才看得到。
