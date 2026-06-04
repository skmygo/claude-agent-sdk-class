# 18 — 檔案系統設定與記憶：CLAUDE.md、commands、agents

## 觀念

前 17 課，所有設定都寫在 Python 的 `ClaudeAgentOptions` 裡。但 Claude Code 還有一套**基於檔案系統**的設定——這也是 Claude Code CLI 與 SDK「共用同一套配置」的關鍵。

最重要的用途是**記憶**：把專案知識寫進 `CLAUDE.md`，agent 每次啟動自動讀到，不必每次在 prompt 裡重講「我們的風格是…、吉祥物叫…」。

```
.claude/
  ├─ commands/  ──► 自訂 slash 指令
  ├─ agents/    ──► 子代理（第 10 課的檔案版）
  └─ skills/    ──► 技能
CLAUDE.md       ──► 專案記憶（自動注入系統提示）
```

## setting_sources：載入哪些來源

| 值 | 載入 | 位置 |
|----|------|------|
| `"user"` | 全域使用者設定 | `~/.claude/` |
| `"project"` | 專案層級（最常用） | 專案 `.claude/` + `CLAUDE.md` |
| `"local"` | 本機私有設定 | gitignore 的本機設定 |

三種設定方式：

```python
setting_sources=None              # 不設 = 載入 CLI 全部預設來源（user+project+local）
setting_sources=[]                # 空陣列 = 完全不載入檔案系統設定
setting_sources=["project"]       # 只載入專案層級
```

## 這課怎麼示範記憶

本資料夾放了一個 `CLAUDE.md`，裡面寫了「吉祥物叫阿露、風格用繁中註解」。`main.py` 設 `cwd` 指向本資料夾、`setting_sources=["project"]`，然後問 Claude 這些事——它會**從 CLAUDE.md 記得**，而不是瞎猜。

`SystemMessage(init)` 的 `data` 也會列出載入了哪些 `slash_commands`、`agents`，可用來驗證設定真的生效。

## 重要觀念

- **`CLAUDE.md` = 跨 session、跨程序的「靜態記憶」**：對照第 09 課的 session（動態對話記憶），CLAUDE.md 是你「手寫、版本控管」的長期知識。
- **預設行為要小心**：`setting_sources` 不設時會載入**所有**來源——包含使用者全域設定。要可重現的乾淨環境，明確指定（甚至用 `[]`）。
- **inline 與檔案版可並存**：第 10 課的 `agents={...}`（Python inline）與 `.claude/agents/*.md`（檔案）會合併。
- **這是 SDK 與 CLI 的橋樑**：同一個 `.claude/` 既給你 `claude` CLI 用，也給 SDK 用，團隊配置一次到位。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

Claude 會答出「吉祥物是阿露」「風格是繁中註解、加 type hint…」——這些它都從 `CLAUDE.md` 讀來。
