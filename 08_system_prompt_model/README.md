# 08 — 系統提示・模型・認證

## 觀念

到目前為止我們都用「裸的」Claude。這課把 agent 的三個身分維度設起來：

```
system_prompt  →  人設與規則（它「是誰、該怎麼做」）
model          →  腦袋（用哪顆模型，貴/快取捨）
認證 (BYOK)     →  身分（透過誰的帳付費、走哪個雲）
```

## system_prompt 的三種寫法

| 寫法 | 範例 | 效果 |
|------|------|------|
| 純字串 | `"你是海盜…"` | 完全自訂人設，**不含**內建工具守則 |
| preset | `{"type": "preset", "preset": "claude_code"}` | 沿用 Claude Code 完整系統提示（教 agent 怎麼用內建工具） |
| preset + append | 上面再加 `"append": "…"` | 內建提示 + 你的補充規則 |

**怎麼選**：要它當「會用工具的程式助手」→ 用 preset；要它扮演特定角色/語氣 → 用字串或 preset+append。

## model 與 fallback

```python
ClaudeAgentOptions(
    model="claude-haiku-4-5",          # 別名也可："haiku" / "sonnet" / "opus"
    fallback_model="claude-sonnet-4-5", # 主模型過載/不可用時自動頂上
)
```

- **別名 vs 完整 id**：`"sonnet"` 這種別名會對應到當前推薦版本；要釘死版本就用完整 id。
- **不設 model**：用 Claude Code 的預設模型。
- **`fallback_model`**：生產環境強烈建議設，避免主模型 529 過載時整個掛掉。

## 認證（BYOK）：改環境變數，不改程式碼

| 供應者 | 環境變數 |
|--------|---------|
| Claude API（預設） | `ANTHROPIC_API_KEY=sk-ant-...` |
| Amazon Bedrock | `CLAUDE_CODE_USE_BEDROCK=1` + AWS 認證 |
| Google Vertex AI | `CLAUDE_CODE_USE_VERTEX=1` + GCP 認證 |
| Microsoft Azure | `CLAUDE_CODE_USE_FOUNDRY=1` + Azure 認證 |

也可以用 `ClaudeAgentOptions(env={...})` 在程式內注入這些環境變數（第 15 課就用這招打開遙測），方便針對單一 agent 切換供應者。

## 重要觀念

- **preset 才會帶內建工具守則**：純字串 system_prompt 雖然自由，但 Claude 可能不知道內建工具怎麼用得最好。要做「程式助手」優先 preset。
- **system_prompt 改的是行為，不是權限**：能不能用工具仍由 `allowed_tools` / `can_use_tool` 決定。
- **per-agent 也能各設模型**：子代理（第 10 課）的 `AgentDefinition(model=...)` 可以讓不同角色用不同模型，省錢又對症下藥。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

四段示範會分別印出海盜腔、預設、附冷知識、以及指定模型的回答。
