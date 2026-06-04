# 02 — 訊息型別：讀懂 Agent 吐出的訊息流

## 觀念

第 01 課我們只挑了 `AssistantMessage` 和 `ResultMessage`。但一個會用工具的 agent，吐出來的訊息其實是一齣有來有回的戲：

```
SystemMessage(init)            ← 開場：給你 session_id、可用工具清單
   ↓
AssistantMessage               ← Claude：「我要用 Bash 跑這個指令」(ToolUseBlock)
   ↓
UserMessage                    ← 系統：把工具執行結果回填 (ToolResultBlock)
   ↓
AssistantMessage               ← Claude：「結果是…」(TextBlock)
   ↓
ResultMessage                  ← 收尾：成本、回合數、最終結果
```

看懂這個流，你才有能力做日誌、做 UI、做除錯。後面講 hooks、可觀測性、子代理追蹤，全都建立在「分辨訊息型別」這個基本功上。

## 四種訊息與內容區塊

| 訊息型別 | 什麼時候出現 | 關鍵欄位 |
|---------|------------|---------|
| `SystemMessage` | 開場 (`subtype=="init"`) 及一些系統事件 | `subtype`、`data`（含 `session_id` / `tools` / `model`…） |
| `AssistantMessage` | Claude 每次發言 | `content`（區塊清單）、`model` |
| `UserMessage` | 工具結果回填、或你送的訊息 | `content` |
| `ResultMessage` | 整個任務結束（只有一則） | `subtype`、`total_cost_usd`、`num_turns`、`result`、`usage` |

`content` 裡的「內容區塊」(ContentBlock) 有四種：

| 區塊 | 意義 |
|------|------|
| `TextBlock` | 純文字（`.text`） |
| `ToolUseBlock` | Claude 決定呼叫工具（`.name`、`.input`、`.id`） |
| `ToolResultBlock` | 工具執行結果（`.tool_use_id`、`.content`、`.is_error`） |
| `ThinkingBlock` | 思考過程（`.thinking`，開啟 thinking 時才有） |

## 重要觀念

- **`isinstance` 是讀訊息流的標準姿勢**：SDK 的訊息與區塊都是 dataclass，用 `isinstance` 分流最清楚。
- **一則 `AssistantMessage` 可以混多種區塊**：Claude 可能「先說一句話、再呼叫工具」，所以一定要走訪整個 `content`。
- **`SystemMessage.data` 是一個百寶箱**：`session_id`（第 09 課續談要用）、`tools`、`slash_commands`、`agents`、`model` 都在這裡。
- **`ResultMessage.subtype`** 告訴你結束的原因：正常結束是 `"success"`，超預算是 `"error_max_budget_usd"`（第 16 課）。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

跑起來會看到 `[system/init]` → `[assistant/tool_use]` → `[user/tool_result]` → `[assistant/text]` → `[result]` 的完整流。
