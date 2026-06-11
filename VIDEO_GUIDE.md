# 上課影片 × 19 課程式實跑指南

> 用法：影片（presentation，共 11 章）每播完一章就暫停，照本指南跑對應的課給學員看。
> 每課列出三件事：**怎麼跑**、**現場看點**（畫面上指給學員看什麼）、**影片沒講到的補充**（講師口頭補上）。

## 章節 ↔ 課程對照總表

| 影片章節 | 主題 | 播完跑這幾課 |
|---------|------|------------|
| 01 coldopen | 開場：沒有新概念 | （不跑，純開場） |
| 02 what-is-it | SDK 是什麼、agent 迴圈 | **01** |
| 03 messages | 訊息流四型別、串流 | **02 → 03** |
| 04 permissions | 權限三層、can_use_tool | **04** |
| 05 tools-mcp | MCP、自訂工具、hooks | **07 → 05 → 06**（照影片敘事順序） |
| 06 config | system_prompt、model、認證 | **08** |
| 07 sessions | resume、fork | **09** |
| 08 subagents | 子代理全套 | **10 → 11 → 12 → 13** |
| 09 production | 成本、遙測、限制 | **14 → 15 → 16** |
| 10 safety-memory | 沙箱、CLAUDE.md、壓縮 | **17 → 18 → 19** |
| 11 closing | 收尾 CTA | （帶學員任挑一課改參數重跑） |

19 課全數被影片覆蓋到「觀念層」，但有些 API 細節影片刻意不講（節奏考量），**這些細節就是你 demo 時的價值所在**——逐課列在下面的「補充」裡。

## 課前準備（上課前一天自己先全部跑一遍）

```bash
pip install claude-agent-sdk        # 本系列對齊 0.2.89；需 Python 3.10+
export ANTHROPIC_API_KEY=sk-ant-...
node --version                       # SDK 底層會啟動 Claude Code CLI 子程序，沒 Node 跑不起來
```

- 第 07 課會用 `npx` 現場下載官方 filesystem MCP server，**教室要有網路**；可先跑一次讓 npx 快取住。
- 第 15 課預設把遙測送到 `localhost:4317`，教室沒有 OTLP collector 就先把 `main.py` 裡的 exporter 改成 `"console"`（檔內已有註解提示）。
- 第 19 課的 PreCompact **短對話不會觸發**——demo 跑的是「接線」，要先跟學員講清楚（見該課補充）。
- 課程 README 明言：範例程式以「能講清楚」為目標，不以實際執行驗證為前提——所以**務必預跑**，現場才不會踩版本差異。

---

## 第 02 章「SDK 是什麼」播完 → 跑 01_hello_world

**影片講到了**：終端 `claude` 背後的 agent 迴圈、SDK 把引擎包成 Python 套件、與 Client SDK 的差別（誰寫工具迴圈）、那 4 行 `query()`。

```bash
cd 01_hello_world && python main.py
```

**現場看點**
- 影片裡那 4 行程式碼，就是這支檔案的骨架——指給學員看 `query()` + `async for`。
- 問的是 `2 + 2`，沒用工具，但訊息流的「形狀」跟複雜任務完全一樣。

**影片沒講，口頭補充**
- `pip install` 之外**還需要 Node.js**：SDK 底層其實是啟動 Claude Code CLI 當子程序，Python 只是駕駛座。
- SDK 全程非同步，入口一定是 `asyncio.run(...)`（要換 `anyio` 也行）。
- `query()` 回傳的不是字串，是**訊息流**；文字藏在 `AssistantMessage.content`（一個 list）裡的 `TextBlock`——所以要走訪。
- `ResultMessage.total_cost_usd` 在某些計費模式下可能是 `0`/`None`，正式程式記得防呆。

---

## 第 03 章「訊息流」播完 → 跑 02_message_types、03_streaming

**影片講到了**：四種訊息（System / Assistant / User / Result）、TextBlock / ToolUseBlock / ToolResultBlock、用 `isinstance` 分流、`include_partial_messages` 串流打字機。

### ▶ 02_message_types

```bash
cd 02_message_types && python main.py
```

**現場看點**
- 這課故意給「需要動用工具」的任務，終端會把影片講的那齣戲完整演一遍：`SystemMessage(init)` → `AssistantMessage(ToolUseBlock)` → `UserMessage(ToolResultBlock)` → `AssistantMessage(TextBlock)` → `ResultMessage`。
- 對照影片：「你在終端用眼睛分，SDK 裡用 isinstance 分」。

**影片沒講，口頭補充**
- 內容區塊其實有**第四種：`ThinkingBlock`**（`.thinking`），開啟 thinking 時才出現——影片只講了三種。
- `SystemMessage` 不只開場一則：要認 `subtype == "init"` 才是開場那則（session_id、工具清單、模型都在 `data` 裡）。
- `UserMessage` 除了工具結果回填，也可能是你自己送進去的訊息。
- `ResultMessage.result` 是最終結果字串，做自動化時直接拿這個欄位最省事。

### ▶ 03_streaming

```bash
cd 03_streaming && python main.py
```

**現場看點**
- 打字機效果本人。對照影片最後一個 step：「終端裡一個字一個字蹦出來的，就是這個」。

**影片沒講，口頭補充**
- `StreamEvent` 是**額外的、不是取代**：開了之後完整的 `AssistantMessage` 和 `ResultMessage` 照樣會到，串流只是讓你「提早」看到文字。
- 解析是兩層判斷：`event["type"] == "content_block_delta"` → `delta["type"] == "text_delta"`（看 `main.py` 的 `text_delta()`）。
- 即時輸出要 `print(chunk, end="", flush=True)`，忘了 `flush` 就不像打字機了。

---

## 第 04 章「權限」播完 → 跑 04_permissions

**影片講到了**：`allowed_tools` / `disallowed_tools` 白名單、`permission_mode` 四值（default / acceptEdits / plan / bypassPermissions）、`can_use_tool` 三岔路（准 / 不准 / 改參數再准）、把 `/etc` 改寫到安全資料夾。

```bash
cd 04_permissions && python main.py
```

**現場看點**
- 影片說的「偷偷改寫」就在這：所有寫檔被導進 `./safe_output/`，跑完開資料夾給學員看。
- `PermissionResultDeny(message=...)` 的理由會回到模型手上，它會換個方式做事。

**影片沒講，口頭補充（這課的補充最重要）**
- **大坑：`permission_mode` 必須是 `"default"`，`can_use_tool` 才會被呼叫**。切到 `acceptEdits` / `bypassPermissions`，你的守門員根本不會上場。影片完全沒提，學員自己寫一定踩。
- callback 是 **async** 的：裡面可以查資料庫、call API、甚至跳一個 UI 問真人，再回傳決定。
- 第三個參數 `context: ToolPermissionContext` 帶額外線索：`context.suggestions`（CLI 建議的權限規則）、`context.blocked_path`。
- 跟 hooks 的分工：`can_use_tool` 只管「准不准用工具」；hooks（06 課）管的是整個生命週期的更多時間點。

---

## 第 05 章「工具與 MCP」播完 → 跑 07_external_mcp、05_custom_tools、06_hooks

**影片講到了**：`mcp_servers` dict 掛官方 filesystem、`mcp__fs__read_file` 命名格式、`@tool` + `create_sdk_mcp_server` 兩個裝飾器、hooks 與 `HookMatcher` 的存在。

> 順序說明：影片是先講「掛別人的 MCP」再講「寫自己的工具」最後 hooks，所以 demo 照 07 → 05 → 06 跑，學員銜接最順。

### ▶ 07_external_mcp

```bash
cd 07_external_mcp && python main.py    # 會 npx 下載官方 filesystem server，需網路
```

**現場看點**
- 影片那串「npx 的設定」就是這裡的 `mcp_servers={"fs": {"command": "npx", ...}}`。
- 跑起來後指出工具全名 `mcp__fs__list_directory`——影片說「你在終端的 MCP 工具也是這個命名，只是你沒仔細看過」。

**影片沒講，口頭補充**
- 傳輸型態有**三種**：`stdio`（本地子程序，最常見、不用寫 type）、`http`、`sse`（遠端服務，要寫 `type` + `url` + `headers`）。
- `mcp_servers` 的 value 放 dict 是外部 server、放 `create_sdk_mcp_server(...)` 物件是進程內 server——**同一個 dict 可以混用**，一個 agent 同時掛兩種。

### ▶ 05_custom_tools

```bash
cd 05_custom_tools && python main.py
```

**現場看點**
- 影片說「兩個裝飾器就搞定」——指給學員看 `@tool` 標記、`create_sdk_mcp_server` 打包、`mcp_servers` 掛載這三步。
- 給工具的那句說明（description），就是 Claude 判斷「何時用它」的依據。

**影片沒講，口頭補充**
- **回傳格式是固定的**：`{"content": [{"type": "text", "text": "..."}]}`；出錯時加 `"is_error": True`，模型會看到錯誤並自行調整。
- **`allowed_tools` 要寫全名** `mcp__toolbox__add` 才放行得了——只寫 `add` 沒用，每次呼叫都卡權限。
- 參數 schema 兩種寫法：簡寫 dict（`{"a": float}`）夠用就好；要描述、巢狀、驗證就上 TypedDict / 完整 JSON Schema。

### ▶ 06_hooks

```bash
cd 06_hooks && python main.py
```

**現場看點**
- 影片只說「插一段自己的程式碼」——這課把它跑活：PreToolUse 擋下危險指令、PostToolUse 審查輸出，終端會印出 hook 被觸發的時刻。

**影片沒講，口頭補充（影片在這裡刻意講得最少，demo 要補最多）**
- 回呼簽名固定三個參數：`async def hook(input_data, tool_use_id, context)`；回傳 dict 控制行為，**回傳 `{}` 就是「不干預」**。
- `HookMatcher(matcher="Bash")` 的 matcher 支援 regex（`"Edit|Write"`）；`None` = 不限工具。
- 事件比影片提的多：`PreToolUse`、`PostToolUse`、`UserPromptSubmit`（注入時間 / 專案規則）、`SessionStart`（載入記憶）、`Stop` / `SubagentStop`、`PreCompact`（19 課回收）。
- hook 的回傳值能做到「擋下」「改寫」「注入 additionalContext」——它是稽核日誌、安全策略、自動修正的基礎建設。

---

## 第 06 章「設定檔」播完 → 跑 08_system_prompt_model

**影片講到了**：`system_prompt` 三種寫法（字串 / preset / preset+append）、`model` 別名與 `fallback_model`、BYOK 環境變數切 Bedrock / Vertex / Azure。

```bash
cd 08_system_prompt_model && python main.py
```

**現場看點**
- 三種 system_prompt 跑出來的「人設差異」直接看得到。
- 影片說「CLAUDE.md 感覺上就是這個 append」——在這裡呼應一下，18 課會真的接起來。

**影片沒講，口頭補充**
- **純字串寫法不含內建工具守則**：agent 會「不太會用工具」。要它當會用工具的程式助手 → 用 preset；要特定角色語氣 → 字串或 preset+append。這是選擇邏輯，影片只列了選項。
- 別名（`"sonnet"` / `"haiku"` / `"opus"`）對應「當前推薦版本」，會隨時間浮動；生產要釘死就用完整 model id。
- `fallback_model` 生產環境**強烈建議設**：主模型 529 過載時自動頂上，不然整個服務跟著掛。
- BYOK 具體變數：`ANTHROPIC_API_KEY`（預設）／`CLAUDE_CODE_USE_BEDROCK=1`／Vertex、Azure 各有對應變數（見本課 README 的表）。同一份程式碼，零修改換雲。

---

## 第 07 章「Session」播完 → 跑 09_sessions

**影片講到了**：從 `SystemMessage(init)` 撈 `session_id`、`resume` 接回去、`fork_session` 分叉平行支線。

```bash
cd 09_sessions && python main.py
```

**現場看點**
- 經典橋段：第一輪告訴它「幸運數字是 7」，第二輪 `resume` 後問「幸運數字是多少」——它記得。沒 resume 的對照組則一臉茫然。
- fork 之後兩條支線各自發展，原線不動。

**影片沒講，口頭補充**
- **`continue_conversation=True`**：接續「最近一次」對話，不必自己記 session_id——CLI 式連續操作最好用。影片只講了終端的 `--continue`，沒講 SDK 這個對應選項。
- `resume` 是**接在原線上繼續**（會改到原 session）；要「不污染原本的」才需要 `fork_session=True`。試多種走法 = 同一個 id fork 多次。
- session_id 的取法寫一次給學員看：`message.data["session_id"]`（在 `subtype == "init"` 那則）。

---

## 第 08 章「子代理」播完 → 跑 10 → 11 → 12 → 13

**影片講到了**：`AgentDefinition` 四欄、description 是寫給主 agent 看的觸發條件、要放行 `"Agent"` 工具、**camelCase vs snake_case 大坑**、拆子代理兩理由（上下文隔離 / 最小權限）、`mcpServers` 專屬工具箱、`parent_tool_use_id` + SubagentStart/Stop 溯源。這章影片講得最完整，demo 重點是「把四課的層次感跑出來」。

### ▶ 10_custom_agents（基礎：定義與委派）

```bash
cd 10_custom_agents && python main.py
```

**現場看點**
- 主 agent 像專案經理，把活外包給 code-reviewer / doc-writer——終端能看到委派發生。
- 指一下 `allowed_tools` 裡的 `"Agent"`：影片說「委派這個動作本身，也是一個工具」。

**口頭補充**：`description`、`prompt` 是必填；`model` 不設就繼承主 agent 的。

### ▶ 11_agent_tool_scoping（切權限）

```bash
cd 11_agent_tool_scoping && python main.py
```

**現場看點**
- analyst 只有唯讀、editor 不准 Bash、runner 只能跑——「想做壞事也沒有工具可用」。
- **現場演影片講的那個坑**：把 `disallowedTools` 改成 `disallowed_tools` 再跑一次——不報錯、靜默失效，權限沒鎖上。這是全系列最值得現場演的一個錯誤。

**口頭補充**
- `tools`（白名單）和 `disallowedTools`（黑名單）可並用：白名單框大範圍，黑名單戳掉個別危險項。
- 子代理權限 ⊆ 主 agent 環境，只會更窄不會更寬。
- 縱深防禦拼圖：11 課的 `tools` 是「結構性限權」，04 課的 `can_use_tool` 是「執行時把關」，兩層疊著用。

### ▶ 12_agent_mcp_servers（各掛各的工具箱）

```bash
cd 12_agent_mcp_servers && python main.py
```

**現場看點**
- weather-bot 只看得到天氣工具、math-bot 只看得到計算工具——影片末尾那一句「靠 mcpServers 指定它掛哪幾個」的完整版。

**口頭補充**：`mcpServers` 兩種寫法——名稱字串（引用 `options.mcp_servers` 全域定義，最常用）或 inline dict（agent 內聯定義）。影片只有一句帶過,模式記法是「全域定義一次，各 agent 各取所需」。

### ▶ 13_subagent_tracking（誰在做事）

```bash
cd 13_subagent_tracking && python main.py
```

**現場看點**
- 終端逐則標出「主 agent / 子代理(id)」——影片講的 `parent_tool_use_id` 溯源，眼見為憑。
- SubagentStart / SubagentStop 印出每個子代理的開工收工。

**口頭補充**
- 同一個子代理的**所有訊息共用同一個** `parent_tool_use_id`，所以能把訊息歸組、畫出活動軌跡。
- SubagentStart/Stop 是「非工具」事件，`HookMatcher` 不必設 matcher（預設 `None` = 不篩）。

---

## 第 09 章「上生產線」播完 → 跑 14 → 15 → 16

**影片講到了**：`ResultMessage` 成本儀表板、`model_usage` 按模型拆帳、OTel 環境變數注入與 OTLP fan-out、console exporter、三道閘門（`max_turns` / `max_budget_usd` / 1M beta）。

### ▶ 14_observability（單次執行報告）

```bash
cd 14_observability && python main.py
```

**現場看點**
- 一份攤平的執行報告：總花費、token 明細（含 cache 讀寫）、回合數、耗時、`model_usage`。
- 影片梗回收：「子代理偷偷用了貴的模型？這裡抓得出來」——指 `model_usage`。

**影片沒講，口頭補充**
- `stderr` callback：底層 CLI 的警告走 stderr，`ClaudeAgentOptions(stderr=my_logger)` 接住，除錯神器。
- 要更詳盡的 log：`extra_args={"debug-file": "/path/to/log"}`。
- `permission_denials` 欄位記錄被拒的工具呼叫——和 04 課的守門員對上了。
- `duration_ms`（總耗時）vs `duration_api_ms`（純 API 耗時），差值就是工具執行時間。

### ▶ 15_otel_telemetry（組織級監控）

```bash
cd 15_otel_telemetry && python main.py
# 教室沒有 OTLP collector → 先把 main.py 裡兩個 EXPORTER 改成 "console"
```

**現場看點**
- console 模式下指標直接印在終端——影片說「想先看效果又懶得架收集器」的那條路。

**影片沒講，口頭補充**
- 影片只說「那幾個環境變數」，具體名字在這課：`CLAUDE_CODE_ENABLE_TELEMETRY=1`（總開關）、`OTEL_METRICS_EXPORTER` / `OTEL_LOGS_EXPORTER`、`OTEL_EXPORTER_OTLP_PROTOCOL`、`OTEL_EXPORTER_OTLP_ENDPOINT`。
- 除錯時把 `OTEL_METRIC_EXPORT_INTERVAL` 調短（預設 60 秒，demo 等不了）——本課 main.py 已設 10 秒。
- 後端要驗證就補 `OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer <token>"`。
- 核心觀念對齊影片：14 課是「跑完一次自己讀」，15 課是「上萬次呼叫的組織級問題」。

### ▶ 16_context_limits（三道閘門）

```bash
cd 16_context_limits && python main.py
```

**現場看點**
- demo 給一個很緊的預算，現場觸發 `error_max_budget_usd`——影片講的「超了就停、狀態變 error_max_budget_usd」眼見為憑。

**影片沒講，口頭補充**
- **預算是「軟煞車」不是精準上限**：檢查發生在「每次 API 呼叫完成後」，最終成本可能比上限略高一個呼叫的量。
- 觸發方式是「正常結束 + subtype 變錯誤碼」，**不是丟例外**——錯誤處理要寫在 ResultMessage 分支裡。
- 1M beta 的確切旗標字串：`betas=["context-1m-2025-08-07"]`；它擴大「裝得下多少」，不改變「裝滿會壓縮」——壓縮的事 19 課接手。

---

## 第 10 章「沙箱與記憶」播完 → 跑 17 → 18 → 19

**影片講到了**：縱深防禦五道牆（cwd / add_dirs / disallowed_tools / permission_mode / can_use_tool）、OS 層級 sandbox、CLAUDE.md 即長期記憶、`setting_sources` 三層與「不設=全載」的預設陷阱、PreCompact 保護指示、`session_store` 換後端。

### ▶ 17_safety_sandbox

```bash
cd 17_safety_sandbox && python main.py
```

**現場看點**
- 結構牆 + 執行牆雙保險：`disallowed_tools=["Bash"]` 讓它根本沒 shell，`can_use_tool` 再逐一查路徑。
- 試著讓它寫沙箱外的路徑，看被擋下。

**影片沒講，口頭補充**
- 實作細節：路徑要 **`resolve()` 成絕對路徑再比對**，才防得住 `../../etc/passwd` 這種穿越——直接字串比對會被繞過。
- 再提醒一次雙胞胎：這裡的 `disallowed_tools` 是 snake_case（`ClaudeAgentOptions`），11 課的 `disallowedTools` 是 camelCase（`AgentDefinition`）。
- 影片那句「更硬的 sandbox 選項」= `ClaudeAgentOptions(sandbox=SandboxSettings(...))`，OS 層級隔離，處理完全不可信輸入時疊上去。

### ▶ 18_filesystem_memory

```bash
cd 18_filesystem_memory && python main.py
```

**現場看點**
- 本課資料夾藏了一個 CLAUDE.md（吉祥物叫阿露）。`main.py` 設 `cwd` + `setting_sources=["project"]`，問它吉祥物是誰——**它從 CLAUDE.md 記得，不是瞎猜**。
- 影片金句落地：「同一個 .claude 資料夾，你的終端在用，你的 SDK agent 也在用」。

**影片沒講，口頭補充**
- `setting_sources` 三種設法語意完全不同：`None`（不設）= 載入**全部**來源（含你個人全域設定，影片提的陷阱）；`[]` = **完全不載**；`["project"]` = 只載專案層。生產建議顯式給值。
- 驗證設定真的生效：看 `SystemMessage(init)` 的 `data` 裡列出的 `slash_commands`、`agents`。
- `.claude/` 底下還有 `commands/`（自訂 slash 指令）、`agents/`（10 課子代理的檔案版）、`skills/`。

### ▶ 19_advanced_persistence

```bash
cd 19_advanced_persistence && python main.py
```

**現場看點（先打預防針）**
- **PreCompact 在短 demo 裡不會觸發**——它只在對話長到逼近上限時才進來。這課 demo 的是「接線」：hook 掛上了、session_store 換掉了，程式正常跑。先講明，學員才不會以為 demo 壞了。

**影片沒講，口頭補充**
- PreCompact 回傳格式：`{"hookSpecificOutput": {"hookEventName": "PreCompact", "additionalContext": "務必保留…"}}`——「插一句話」的具體寫法。
- `input_data["trigger"]` 分 `"auto"`（SDK 自動壓縮）和 `"manual"`（使用者下 `/compact`）。
- 影片說「換掉 session_store 就行」：demo 用內建 `InMemorySessionStore` 示範形狀；生產換 Redis / Postgres / S3，照官方 `examples/session_stores` 實作 `SessionStore` 介面。
- 收束對照：09 課管「怎麼存、怎麼續」，19 課管「存到哪、壓縮時保住什麼」。

---

## 第 11 章收尾後的互動環節

影片 CTA 就是這個課程資料夾本身。建議現場：

1. 讓學員任選「今天剛聽過」的一課，改兩個參數重跑——例如把 04 課的 safe_output 改名、把 08 課的 model 換成 haiku、把 16 課的預算調更緊。
2. 重演 11 課那個 camelCase 坑當壓軸：寫錯不報錯、靜默失效——「權限沒鎖上，最危險」。
3. 提醒影片最後那句話：你跟用 SDK 寫 agent 的人之間，差的只是 `from claude_agent_sdk import query`。

## 附：影片覆蓋度速查（講師備忘）

| 課 | 影片覆蓋 | demo 必補的一件事 |
|----|---------|------------------|
| 01 | ✅ 充分 | 需要 Node.js；async 入口 |
| 02 | ✅ 充分 | ThinkingBlock 第四種區塊 |
| 03 | ✅ 充分 | StreamEvent 是「額外」不是「取代」 |
| 04 | ✅ 充分 | **can_use_tool 只在 permission_mode="default" 生效** |
| 05 | 🟡 觀念有、細節無 | 回傳格式固定 + allowed_tools 要全名 |
| 06 | 🟡 點到為止 | 回呼簽名 / 回傳 dict / matcher regex / 事件全表 |
| 07 | ✅ 充分 | stdio / http / sse 三種傳輸；可混用 |
| 08 | ✅ 充分 | 純字串不含工具守則；別名會浮動 |
| 09 | ✅ 充分 | continue_conversation=True |
| 10 | ✅ 充分 | description / prompt 必填；model 繼承 |
| 11 | ✅ 充分（坑都講了） | 現場演一次靜默失效 |
| 12 | 🟡 一句帶過 | mcpServers 兩種寫法；全域定義一次各取所需 |
| 13 | ✅ 充分 | 同 id 歸組；非工具事件不設 matcher |
| 14 | ✅ 充分 | stderr callback / permission_denials |
| 15 | 🟡 觀念有、變數名無 | 具體 env 名；console 後備；export interval |
| 16 | ✅ 充分 | 預算是軟煞車；不丟例外 |
| 17 | ✅ 充分 | resolve() 絕對路徑防穿越 |
| 18 | ✅ 充分 | setting_sources 三種設法的語意差 |
| 19 | ✅ 充分 | 短 demo 不觸發 PreCompact（先打預防針） |
