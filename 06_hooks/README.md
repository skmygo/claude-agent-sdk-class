# 06 — 生命週期 Hooks：在關鍵時刻插入你的程式碼

## 觀念

第 04 課的 `can_use_tool` 只管「准不准用工具」。Hooks 管的範圍更廣——它讓你在 agent 生命週期的**好幾個時間點**插入程式碼：

```
使用者送出 prompt ──[UserPromptSubmit]──► 工具即將執行 ──[PreToolUse]──►
   工具實際執行 ──[PostToolUse]──► …重複… ──► 結束 ──[Stop]
                                            壓縮前 ──[PreCompact]
```

每個時間點都能：記錄、驗證、阻擋、改寫、注入脈絡。這是做稽核日誌、安全策略、自動修正的基礎建設。

## 常用事件

| 事件 | 觸發時機 | 典型用途 |
|------|---------|---------|
| `PreToolUse` | 工具執行前 | 擋危險操作、改寫參數 |
| `PostToolUse` | 工具執行後 | 審查輸出、出錯時提示模型 |
| `UserPromptSubmit` | 使用者送出 prompt | 注入時間、專案規則等脈絡 |
| `SessionStart` | session 開始 | 載入記憶、設定初始脈絡 |
| `Stop` / `SubagentStop` | 主/子代理結束 | 收尾、驗證任務完成 |
| `PreCompact` | 上下文壓縮前 | 保護重要資訊（見第 19 課） |

## 怎麼掛 hook

```python
options = ClaudeAgentOptions(
    hooks={
        "PreToolUse": [HookMatcher(matcher="Bash", hooks=[my_hook])],
    }
)
```

- `matcher`：篩工具名，支援 regex（`"Edit|Write"`）；`None` = 不限工具。
- `hooks`：一串回呼，依序執行。
- 回呼簽名固定：`async def hook(input_data, tool_use_id, context)`。

## 回呼回傳什麼（決定行為）

回傳一個 dict，常見欄位：

| 你想做 | 回傳 |
|--------|------|
| 不干預 | `{}` |
| 擋下工具（PreToolUse） | `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}` |
| 工具後補脈絡（PostToolUse） | `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}}` |
| 給使用者一句提示 | `{"systemMessage": "..."}` |
| 直接中止整個任務 | `{"continue_": False, "stopReason": "..."}` |

## Hook vs can_use_tool（怎麼選）

| | `can_use_tool`（第 04 課） | Hooks（本課） |
|---|---|---|
| 管的範圍 | 只有「用工具的權限」 | 整個生命週期多個事件 |
| 時間點 | 工具執行前 | 前、後、prompt、結束、壓縮… |
| 典型用途 | 權限決策、改寫輸入 | 稽核、注入脈絡、流程控制 |

兩者可並用：`can_use_tool` 做權限、hooks 做日誌與脈絡。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

會看到 `ls /not_exist_dir` 出錯後，PostToolUse hook 補上提示；含 `rm -rf` 的指令則被 PreToolUse 直接擋下。
