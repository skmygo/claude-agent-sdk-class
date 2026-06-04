# 04 — 權限控制：can_use_tool 動態守門

## 觀念

第 01–02 課我們用 `allowed_tools` 開了工具，那是「靜態白名單」——只看工具名稱。但真實世界裡，`Bash` 這個工具可以是 `ls`（安全），也可以是 `rm -rf /`（災難）。你需要看著**實際參數**臨場決定。

`can_use_tool` 就是這個臨場守門員。每次 agent 想用工具，SDK 都先把 `(工具名, 輸入, 情境)` 交給你的 callback，你回三種結果之一：

```
        ┌─ PermissionResultAllow()                    放行
申請 ──►├─ PermissionResultAllow(updated_input=...)   改寫參數後放行
        └─ PermissionResultDeny(message="理由")        擋下
```

## 三層權限，由粗到細

| 層級 | 機制 | 看得到什麼 | 適合 |
|------|------|-----------|------|
| 白名單 | `allowed_tools` / `disallowed_tools` | 只有工具名 | 簡單放行/封鎖 |
| 模式 | `permission_mode` | 全域策略 | 一次性放寬/收緊 |
| **回呼** | **`can_use_tool`** | **工具名 + 實際輸入** | **臨場、條件式、改寫** |

`permission_mode` 可選值：

| 值 | 行為 |
|----|------|
| `"default"` | 標準把關（**要用這個，`can_use_tool` 才會被呼叫**） |
| `"acceptEdits"` | 自動接受檔案編輯 |
| `"plan"` | 計畫模式，不實際動手 |
| `"bypassPermissions"` | 全部放行（危險，僅限可信環境） |

## 重要觀念

- **`updated_input` 是殺手鐧**：不是只能 yes/no，你能「消毒」參數——把寫入路徑導去安全資料夾、砍掉危險旗標、補上預設值。範例就示範把所有寫檔導進 `./safe_output/`。
- **callback 是 async 的**：可以在裡面查資料庫、call API、甚至跳出 UI 問使用者，再回傳決定。
- **`context: ToolPermissionContext`** 帶有額外線索，例如 `context.suggestions`（CLI 建議的權限規則）、`context.blocked_path`。
- **和 hooks 的差別**：`can_use_tool` 專責「准不准用工具」；hooks（第 06 課）能管更多生命週期事件（送出 prompt、工具跑完之後、session 開始…）。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

會看到列檔（唯讀，放行）被准、寫檔路徑被改寫進 `safe_output/` 的過程。
