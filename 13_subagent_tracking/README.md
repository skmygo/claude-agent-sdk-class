# 13 — 子代理追蹤：看清楚是誰在做事

## 觀念

多代理協作很強大，但也帶來一個現實問題：所有訊息（主 agent、各子代理）都混在**同一條訊息流**裡。做日誌、做監控、做 UI 時，你得能回答「這一句話，到底是誰說的？」

兩個追蹤工具：

```
parent_tool_use_id   訊息層級的「身分標籤」
   None     → 主 agent
   有值     → 子代理（值 = 發起它的那次 Agent 工具呼叫 id）

SubagentStart / SubagentStop   生命週期 hooks
   標記每個子代理的「開工」與「收工」
```

## 怎麼用 parent_tool_use_id

`AssistantMessage` 和 `UserMessage` 都有這個欄位：

```python
def who(message):
    pid = getattr(message, "parent_tool_use_id", None)
    return "主 agent" if pid is None else f"子代理({pid[:8]}…)"
```

同一個子代理產生的所有訊息，會共用同一個 `parent_tool_use_id`，所以你能把它們歸成一組。

## 怎麼用 Subagent hooks

```python
hooks={
    "SubagentStart": [HookMatcher(hooks=[on_subagent_start])],
    "SubagentStop":  [HookMatcher(hooks=[on_subagent_stop])],
}
```

這兩個是「非工具」事件，所以 `HookMatcher` 不必設 `matcher`（預設 `None` = 不篩）。

## 兩者怎麼搭

| 你想知道 | 用哪個 |
|---------|-------|
| 這則訊息屬於哪個子代理 | `parent_tool_use_id` |
| 子代理什麼時候開始/結束 | `SubagentStart` / `SubagentStop` |
| 完整時間軸（誰、何時、說了什麼） | 兩者結合 |

## 重要觀念

- **`parent_tool_use_id` 是「歸屬」，不是「事件」**：它告訴你訊息屬於誰；hooks 才是時間點事件。
- **這是可觀測性的前置**：第 14、15 課要量化成本/用量，常需要先能「按子代理分組」，靠的就是這個欄位。
- **巢狀也適用**：子代理再叫子代理時，同樣靠 `parent_tool_use_id` 串出階層。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

會看到 `[SubagentStart]` →（一串 `[子代理(...)]` 的發言）→ `[SubagentStop]` → `[主 agent]` 收尾。
