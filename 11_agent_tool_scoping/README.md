# 11 — 子代理工具範圍：每個 agent 各管各的權限

## 觀念

第 10 課我們建了子代理。這課專講一件事：**怎麼把每個子代理的權限切乾淨**。

核心原則是**最小權限（least privilege）**——每個角色只拿到完成工作「剛好夠用」的工具：

```
analyst（分析員）   ─► Read, Grep, Glob          （唯讀，碰不到檔案內容修改）
editor（編輯員）    ─► Read, Write, Edit          但 disallowedTools=["Bash"]（不准跑指令）
runner（執行員）    ─► Bash                       （只負責跑，不負責改）
```

這樣即使某個子代理被惡意 prompt 帶偏，它「想做壞事也沒有工具可用」。

## 白名單 vs 黑名單

| 欄位 | 作用 | 範例 |
|------|------|------|
| `tools` | 白名單：只允許這些 | `["Read", "Grep"]` |
| `disallowedTools` | 黑名單：明確禁止這些 | `["Bash"]`（**camelCase**） |

兩者可並用。一般做法：用 `tools` 框出大範圍，再用 `disallowedTools` 戳掉個別危險項。

## 重要觀念

- **大小寫陷阱（再強調一次）**：`AgentDefinition` 的 `disallowedTools` 是 **camelCase**；`ClaudeAgentOptions` 的 `disallowed_tools` 是 snake_case。寫錯不會報錯，但會「靜默失效」——權限沒鎖到，很危險。
- **子代理權限 ⊆ 你給的範圍**：子代理不會有比主 agent 環境更大的能力。`tools` 是在這個前提下進一步收窄。
- **權限分層回顧**：第 04 課 `can_use_tool`（執行時動態決策）＋ 第 11 課 `tools` 範圍（結構性限權）＝ 縱深防禦。結構先鎖死能用的工具，執行時再臨場把關參數。
- **MCP 工具也能限範圍**：下一課用 `mcpServers` 讓不同子代理連不同的工具箱。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
