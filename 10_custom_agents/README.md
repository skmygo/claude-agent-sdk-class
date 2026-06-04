# 10 — 自訂子代理：把任務委派給專職角色

## 觀念

一個 agent 什麼都做，上下文很快就塞滿、人設也難兼顧。**子代理**讓你把工作拆給專職角色：主 agent 像專案經理，把子任務外包給「code reviewer」「文件作者」「測試員」，各自帶著乾淨的上下文與專屬人設去做，做完回報。

```
主 agent ──委派──► code-reviewer（只給唯讀工具，專心挑問題）
        └─委派──► doc-writer（給讀寫工具，專心寫文件）
```

## 怎麼定義與呼叫

```python
options = ClaudeAgentOptions(
    agents={
        "code-reviewer": AgentDefinition(
            description="…什麼時候該叫它…",   # 主 agent 靠這句決定要不要委派
            prompt="…它的人設與工作守則…",
            tools=["Read", "Grep", "Glob"],
            model="sonnet",
        ),
    },
    allowed_tools=["Read", "Grep", "Glob", "Agent"],   # ← 一定要放行 "Agent"
)
```

兩個重點：
1. **`description` 是觸發條件**：主 agent 讀它來判斷「這個子任務該不該交給你」。寫清楚「何時用」比「是什麼」更重要。
2. **必須放行 `"Agent"` 工具**：委派是透過內建的 `Agent` 工具完成的，沒放行就叫不動。

## AgentDefinition 欄位速查

| 欄位 | 說明 |
|------|------|
| `description` | 何時該用這個子代理（必填） |
| `prompt` | 子代理的系統提示／人設（必填） |
| `tools` | 它能用的工具白名單 |
| `disallowedTools` | 黑名單（注意是 **camelCase**） |
| `model` | 別名或完整 id；不設則繼承 |
| `mcpServers` | 專屬 MCP（**camelCase**，第 12 課） |
| `permissionMode` | 專屬權限模式（**camelCase**） |

> ⚠️ 注意大小寫：`AgentDefinition` 沿用 TypeScript SDK 的命名，`disallowedTools`、`mcpServers`、`permissionMode`、`maxTurns`、`initialPrompt` 是 **camelCase**；而 `ClaudeAgentOptions` 是 snake_case（`disallowed_tools`、`mcp_servers`…）。兩者不要混。

## 為什麼要用子代理

- **上下文隔離**：子代理用自己的上下文視窗，不會把一堆中間產物塞回主對話。
- **權限最小化**：reviewer 只給唯讀工具，從根本上不可能改壞檔案（第 11 課深入）。
- **對症選模型**：簡單活用 haiku、難的用 sonnet/opus，省錢（第 08 課的 per-agent model）。
- **人設專一**：每個角色一套規則，回答品質更穩。

## 重要觀念

- **inline vs 檔案系統**：本課是用 Python 直接定義（inline）。你也可以把 agent 寫成 `.claude/agents/*.md`，用 `setting_sources` 載入（第 18 課）。
- **接下來三課都圍著子代理**：11 限權、12 掛專屬 MCP、13 追蹤誰在做事。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
