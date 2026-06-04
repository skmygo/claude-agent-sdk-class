# Claude Agent SDK (Python) 教學系列

一個觀念一個資料夾，每個範例獨立、由淺入深。學完這 19 課，你能用 Python 把 Claude Code 當成程式庫，做出會自己讀檔、執行指令、搜尋、改程式碼的 AI Agent。

> **SDK 版本：`claude-agent-sdk` 0.2.89**　·　**語言：Python 3.10+**
> 本系列只用 Python 講解；每課的 `main.py` 都對齊官方 [`claude-agent-sdk-python/examples`](https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples) 的寫法，再改寫成更好教學的形式。為聚焦觀念，程式碼以「能講清楚」為目標，不以實際執行驗證為前提。

## 這個 SDK 是什麼

Agent SDK 把 **Claude Code 的核心**（同一套內建工具、agent 迴圈、上下文管理）包成一個程式庫。你寫 prompt，Claude 自己決定要呼叫哪些工具、跑幾輪，直到任務完成：

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="找出 auth.py 的 bug 並修好",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)   # Claude 讀檔、找 bug、改檔，全程自動

asyncio.run(main())
```

對照 **Client SDK**（`anthropic` 套件）：那邊你要自己寫「呼叫模型 → 執行工具 → 把結果餵回去」的迴圈；Agent SDK 幫你把這個迴圈做掉了。

## 前置需求

1. **Python 3.10+**
   ```bash
   python3 --version
   ```
2. **Node.js**（SDK 底層會啟動 Claude Code CLI 子程序）
   ```bash
   node --version
   ```
3. **安裝 SDK**（本專案用 [uv](https://docs.astral.sh/uv/) 管理）
   ```bash
   uv sync                 # 依 pyproject.toml 安裝 claude-agent-sdk + anyio
   # 或
   pip install claude-agent-sdk
   ```
4. **設定認證**：從 [Claude 主控台](https://platform.claude.com/)取得 API Key
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   也支援 Amazon Bedrock / Google Vertex / Azure 等第三方供應者（見 [08 課](08_system_prompt_model/)）。

> 第 07 課的外部 MCP 範例需要額外的 npm 套件（如 `@playwright/mcp`），會在該課說明。

## 教學目錄

| # | 資料夾 | 觀念 | 核心 API |
|---|--------|------|---------|
| 01 | [01_hello_world](01_hello_world/) | 最小可運行範例 — 送一句話、拿到回覆 | `query()` |
| 02 | [02_message_types](02_message_types/) | 訊息流解析 — 四種訊息與內容區塊 | `AssistantMessage` / `TextBlock` / `ResultMessage` |
| 03 | [03_streaming](03_streaming/) | 即時串流輸出 — 逐 token 顯示 | `include_partial_messages` + `StreamEvent` |
| 04 | [04_permissions](04_permissions/) | 權限控制 — 動態允許/拒絕/改寫工具呼叫 | `can_use_tool` + `PermissionResultAllow/Deny` |
| 05 | [05_custom_tools](05_custom_tools/) | 自訂工具 — 把 Python 函式變成 Claude 的工具 | `@tool` + `create_sdk_mcp_server` |
| 06 | [06_hooks](06_hooks/) | 生命週期 Hooks — 攔截與修改 agent 行為 | `hooks` + `HookMatcher` |
| 07 | [07_external_mcp](07_external_mcp/) | 外部 MCP 伺服器 — 接上整個工具生態系 | `mcp_servers`（stdio / http） |
| 08 | [08_system_prompt_model](08_system_prompt_model/) | 系統提示・模型・認證 — 角色、選模型、BYOK | `system_prompt` / `model` / `env` |
| 09 | [09_sessions](09_sessions/) | Session 持久化 — 斷點續談、分叉探索 | `resume` / `continue_conversation` / `fork_session` |
| 10 | [10_custom_agents](10_custom_agents/) | 自訂子代理 — 委派專職角色 | `agents` + `AgentDefinition` |
| 11 | [11_agent_tool_scoping](11_agent_tool_scoping/) | 子代理工具範圍 — 每個 agent 各管各的權限 | `AgentDefinition.tools` / `disallowedTools` |
| 12 | [12_agent_mcp_servers](12_agent_mcp_servers/) | 子代理專屬 MCP — 不同 agent 掛不同工具箱 | `AgentDefinition.mcpServers` |
| 13 | [13_subagent_tracking](13_subagent_tracking/) | 子代理追蹤 — 看清楚是誰在做事 | `parent_tool_use_id` + `SubagentStart/Stop` |
| 14 | [14_observability](14_observability/) | 成本與用量 — token、花費、回合數一覽 | `ResultMessage.usage` / `total_cost_usd` |
| 15 | [15_otel_telemetry](15_otel_telemetry/) | OpenTelemetry 遙測 — 把指標送進可觀測性平台 | `env` + `CLAUDE_CODE_ENABLE_TELEMETRY` |
| 16 | [16_context_limits](16_context_limits/) | 上下文與執行限制 — 回合、預算、1M 上下文 | `max_turns` / `max_budget_usd` / `betas` |
| 17 | [17_safety_sandbox](17_safety_sandbox/) | 安全沙箱 — 把 agent 關進指定資料夾 | `cwd` / `add_dirs` / `permission_mode` |
| 18 | [18_filesystem_memory](18_filesystem_memory/) | 檔案系統設定與記憶 — `CLAUDE.md`、skills、commands | `setting_sources` |
| 19 | [19_advanced_persistence](19_advanced_persistence/) | 進階持久化與壓縮 — 自訂後端、攔截 compact | `SessionStore` + `PreCompact` hook |

## 學習路線圖

- **基礎（01–03）**：怎麼送請求、怎麼讀回來的訊息流、怎麼即時串流。
- **工具與權限（04–07）**：內建工具的權限把關、寫自己的工具、攔截行為、接外部 MCP。
- **設定與狀態（08–09）**：選模型/角色/認證、跨輪次保存對話。
- **子代理（10–13）**：委派、限權、掛專屬工具、追蹤誰在做事。
- **生產化（14–19）**：成本可觀測性、遙測、執行限制、安全沙箱、檔案系統設定與記憶、進階持久化。

## 執行方式

```bash
uv run 01_hello_world/main.py
# 或進到資料夾再跑
cd 01_hello_world && uv run main.py
```

## 兩種進入點：`query()` vs `ClaudeSDKClient`

整個 SDK 的對話有兩種開法，這 19 課會交替使用：

| | `query()` | `ClaudeSDKClient` |
|---|-----------|-------------------|
| 形態 | 函式，回傳 async 迭代器 | 類別，需 `connect()` / `async with` |
| 狀態 | 單次、用完即走 | 持久連線，可多輪對話 |
| 適合 | 一次性任務、批次腳本 | 互動式 App、需要中途 `interrupt()` |
| 出現在 | 01–09、14–19 多數課 | 05、06、10、第 10 課之後的互動範例 |

```python
# query()：一次性
async for message in query(prompt="...", options=options):
    ...

# ClaudeSDKClient：多輪互動
async with ClaudeSDKClient(options=options) as client:
    await client.query("第一輪")
    async for msg in client.receive_response():
        ...
    await client.query("第二輪（記得上一輪）")
    async for msg in client.receive_response():
        ...
```

## 認證方式（BYOK）

SDK 透過環境變數選擇供應者，程式碼不用改（細節見 [08 課](08_system_prompt_model/)）：

| 供應者 | 環境變數 |
|--------|---------|
| Claude API（預設） | `ANTHROPIC_API_KEY` |
| Amazon Bedrock | `CLAUDE_CODE_USE_BEDROCK=1` + AWS 認證 |
| Google Vertex AI | `CLAUDE_CODE_USE_VERTEX=1` + GCP 認證 |
| Microsoft Azure | `CLAUDE_CODE_USE_FOUNDRY=1` + Azure 認證 |

## 參考資源

- 官方文件：<https://code.claude.com/docs/zh-TW/agent-sdk/overview>
- Python API 參考：<https://code.claude.com/docs/zh-TW/agent-sdk/python>
- 官方範例：<https://github.com/anthropics/claude-agent-sdk-python/tree/main/examples>
- 範例 Agent（Email 助手、研究 agent…）：<https://github.com/anthropics/claude-agent-sdk-demos>
