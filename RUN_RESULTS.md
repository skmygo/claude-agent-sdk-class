# 19 課 Haiku 實跑驗證報告

> 把每一課都設定成用 **Haiku** 模型實際跑過，逐課存證；跑不起來的就地修好。
> 本檔即「證明」：每課的真實輸出片段、成本、耗時，以及修了什麼、為什麼。

## 結論

| 項目 | 結果 |
|---|---|
| 驗證日期 | 2026-06-23 |
| 模型 | **`claude-haiku-4-5`**（19 課的每個 `ClaudeAgentOptions` / `AgentDefinition` 都明確指定） |
| 認證 | Claude Code CLI 既有的訂閱 OAuth（無 `ANTHROPIC_API_KEY` 也能跑，SDK 子程序繼承 CLI 登入） |
| SDK 版本 | `claude-agent-sdk` **0.2.107**（教材原以 0.2.89 撰寫，下方坑多來自版本差異） |
| 執行環境 | Python 3.12 / Node v24 / `uv` |
| **可跑課數** | **19 / 19 全部 `exit 0`** ✅ |
| 需要修才能跑 | 7 課（07、10、11、12、13、16、17）+ 1 課可靠性強化（05） |
| 一輪總成本 | 約 **US$0.35**（Haiku，便宜；不印成本的課除外） |

**模型鐵證**：第 14 課會印出 `model_usage`，整輪只出現 `claude-haiku-4-5` 與 `claude-haiku-4-5-20251001`；掃過全部 19 份 log，**沒有任何 `claude-sonnet-*` / `claude-opus-*` 被實際呼叫**。

---

## 怎麼跑的（可重現）

1. 每課的 `model=` 已寫死成 `claude-haiku-4-5`（含第 10–13 課的子代理；第 08 課保留 `fallback_model="claude-sonnet-4-5"` 作為「主模型失敗才退備援」的教學示範，平時不觸發）。
2. 跑的時候再用環境變數把「背景小模型」「sonnet/opus 別名」也全部指向 Haiku，雙保險：

```bash
export ANTHROPIC_MODEL=claude-haiku-4-5-20251001
export ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-haiku-4-5-20251001
export ANTHROPIC_DEFAULT_SONNET_MODEL=claude-haiku-4-5-20251001
export ANTHROPIC_DEFAULT_OPUS_MODEL=claude-haiku-4-5-20251001
export ANTHROPIC_SMALL_FAST_MODEL=claude-haiku-4-5-20251001

# 逐課（在各自資料夾內跑，產出物才落在該課目錄）
cd 01_hello_world && uv run main.py
```

---

## 總表

| # | 課程 | 狀態 | 耗時 | 一句話結果 | 改過？ |
|---|------|:---:|:---:|------|:---:|
| 01 | hello_world | ✅ | 4s | `2 + 2 = 4` |  |
| 02 | message_types | ✅ | 7s | 完整訊息流，Bash 跑 `date` 拿到日期 |  |
| 03 | streaming | ✅ | 6s | 逐 token 串流講出 Python 之禪 |  |
| 04 | permissions | ✅ | 16s | 守門員把寫檔路徑改寫進 `./safe_output/` |  |
| 05 | custom_tools | ✅ | 17s | `get_weather(台北)→28°C`、`add→42` 都實呼叫 | 🔧 隔離 |
| 06 | hooks | ✅ | 18s | PreToolUse 放行、PostToolUse 偵測到錯誤輸出 |  |
| 07 | external_mcp | ✅ | 22s | npx 起 filesystem MCP，列檔＋讀檔 | 🔧 修 |
| 08 | system_prompt_model | ✅ | 29s | 海盜人設／preset／append 冷知識／fallback 四案 |  |
| 09 | sessions | ✅ | 17s | 幸運數字 7 → resume 記得 7 → fork 改 42 |  |
| 10 | custom_agents | ✅ | 25s | code-reviewer 子代理真的做了 code review | 🔧 修 |
| 11 | agent_tool_scoping | ✅ | 14s | analyst 子代理正確列出 imports | 🔧 修 |
| 12 | agent_mcp_servers | ✅ | 11s | weather-bot 查天氣、math-bot 算 12+30=42 | 🔧 修 |
| 13 | subagent_tracking | ✅ | 40s | SubagentStart/Stop 觸發，researcher 回報主題 | 🔧 修 |
| 14 | observability | ✅ | 34s | 印出 token 用量 / `model_usage`（haiku 鐵證） |  |
| 15 | otel_telemetry | ✅ | 8s | 任務完成；OTLP 無 collector 時匯出靜默失敗（不致命） |  |
| 16 | context_limits | ✅ | 26s | max_turns／max_budget 觸發並接住、1M beta 被忽略 | 🔧 修 |
| 17 | safety_sandbox | ✅ | 53s | 🛑 擋下沙箱外、✅ 放行沙箱內，檔案確實落在沙箱 | 🔧 修(安全) |
| 18 | filesystem_memory | ✅ | 7s | 讀專案 CLAUDE.md，答出吉祥物「阿露」水獺 |  |
| 19 | advanced_persistence | ✅ | 10s | InMemorySessionStore + PreCompact hook 就緒 |  |

---

## 修了什麼、為什麼

這次失敗的根因分三類：**SDK 版本行為差異**、**主機全域環境污染**、**一個真的安全 bug**。

### A. SDK 0.2.107 在「錯誤結尾」會丟例外（07、16）

教材原本假設 `max_turns` / `max_budget` 用盡時，SDK 會「吐一則帶 `error_*` subtype 的 `ResultMessage` 讓你自己讀」。但 0.2.107 的行為是 **先吐那則 ResultMessage、緊接著再 `raise Exception`**，沒接住就直接 crash。

- **16_context_limits**：把 `run()` 的 `async for` 包進 `try/except`。三個 case（max_turns、max_budget、1M）現在都跑完，預算上限那段照樣印出 `subtype=error_max_budget_usd`，尾巴的例外被「[收尾例外，已接住]」吃掉。
- **07_external_mcp**：`max_turns=3` 太少（npx 冷啟動 + 列檔 + 讀檔 + 摘要跑不完就撞牆 → raise）。改 `max_turns=6`、`allowed_tools` 補上 `mcp__fs__read_text_file`，並先預熱 npx 套件。

### B. 主機全域設定污染（07、10、11、12、13；05 強化）

這些課原本沒設 `setting_sources`，SDK 預設會**載入使用者全域 Claude Code 設定**——包含這台機器裝的 `dokploy-mcp` 伺服器（約 31 個工具），還會沿目錄往上抓到 `/home/sk/work/CLAUDE.md`（那份 Dokploy 維運大全）。結果：

- **11**：analyst 子代理被叫起來後，整段在介紹「Dokploy API」而不是分析 main.py 的 import。
- **12**：主代理卡在「等待權限核准」那些外部工具，沒真的委派。
- **10 / 13**：haiku 被一堆無關工具 + 上層脈絡帶偏，反問「請給我路徑」而不動手。
- **05**：haiku 在 31 個工具裡選錯，把 `get_weather` 叫歪。

**修法**：替這些課加 `setting_sources=[]`（跑成範例時完全不吃外部設定，hermetic 隔離），第 12 課再把子代理要用的 MCP 工具名補進 `allowed_tools`（比照第 05 課，非互動模式才不會卡權限），第 10/11/13 prompt 講明「就是 `./main.py`，直接做別反問」。**全程沒有用 `bypassPermissions`**（這是一個講安全的教材，不該示範繞過權限）。

> 註：乾淨環境（沒有自訂全域 MCP、沒有上層 CLAUDE.md）跑原版這幾課不會有這問題；`setting_sources=[]` 讓它在「被高度客製化的主機」上也穩定重現。

### C. 第 17 課的安全 bug（沙箱沒關起來）🔴

這是最該記一筆的。原版 17 把 `Write` 放進了 `allowed_tools=["Read", "Write", "Glob"]`。

**Claude Code 權限模型裡，靜態白名單（`allowed_tools`）內的工具會被「預先放行」、直接略過 `can_use_tool`。** 所以沙箱守衛 `confine_to_sandbox` **從來沒被諮詢過 Write** —— 這個「安全沙箱」示範自己沒把沙箱關上。實測模型把 `notes.txt` 寫到了 **沙箱外的 `/home/sk/work/notes.txt`**（第 04 課之所以有效，正是因為它**沒設** `allowed_tools`，全靠 `can_use_tool` 把關）。

**修法**：

1. 把 `Write` 移出 `allowed_tools`（只留 `["Read", "Glob"]`）→ 寫檔不再被預先放行，守衛才真的審查。
2. 守衛加 `print`，讓攔截/放行看得見。
3. 加 `setting_sources=[]`（避免上層 CLAUDE.md 把 haiku 帶去 `/home/sk/work` 寫檔）。
4. `query()` 因為要搭 `can_use_tool`，本來就會報 `requires streaming mode`，一併改成 `ClaudeSDKClient`（見下一點）。

修好後實測：模型先試 `/notes.txt` → `🛑 擋下：路徑超出沙箱`；改寫沙箱內 → `✅ 放行`；檔案確實落在 `sandbox/notes.txt`，沙箱外乾淨。

### D. `can_use_tool` 需要 streaming（17）

`query(prompt="字串", can_use_tool=...)` 會直接報錯 `can_use_tool callback requires streaming mode`。改用 `ClaudeSDKClient`（`async with` + `client.query()` + `receive_response()`，同第 04 課）即可。

---

## 特別說明（不是 bug，但值得知道）

- **15_otel_telemetry「能跑」**：它指向 `http://localhost:4317` 的 OTLP collector。沒有 collector 時，**遙測匯出在背景靜默失敗、不影響主任務**——Claude 照樣完成「數檔案」並正常結束。想真的看到指標，照該課註解把 exporter 改成 `console`，或起一個 collector。
- **16 的 1M 超長上下文在訂閱認證下會被忽略**：log 出現 `Warning: Custom betas are only available for API key users. Ignoring provided betas.`。`betas=["context-1m-2025-08-07"]` 只有用 **API key** 才生效；本機走訂閱 OAuth，所以 beta 被忽略但**請求照常成功**。要實測 1M 請改用 `ANTHROPIC_API_KEY`。
- **成本顯示**：03、08、09、18 那幾課程式碼本來就沒印成本，不是花 $0。

---

## 逐課證據（真實輸出片段）

### 01 hello_world
```
Claude: 2 + 2 = 4.
花費 $0.0035，共 1 回合
```

### 02 message_types
```
[system/init] session=f4ac2f27…  可用工具 31 個
[assistant/tool_use] 呼叫 Bash，輸入={'command': 'date', ...}
[user/tool_result] Tue Jun 23 05:40:36 PM CST 2026…
[result] subtype=success  成本 $0.0239  回合 2
```

### 03 streaming
```
Claude: Python 的設計哲學可以用三句話概括：
1. 簡潔可讀優先 …  2. 明確優於隱晦 …  3. 簡單優於複雜 …
（逐 token 串流輸出，最後換行收尾）
```

### 04 permissions
```
🛂 申請使用 Write：{'file_path': '…/04_permissions/note.txt', 'content': 'hello'}
   ⚠️  把寫入路徑從 …/note.txt 改寫成 ./safe_output/note.txt
```
> 實測檔案落在 `04_permissions/safe_output/note.txt`，原指定路徑沒被寫到。

### 05 custom_tools 🔧
```
  [工具被呼叫] get_weather(city='台北') → 28°C 多雲
Claude: 台北天氣：28°C，多雲 ☁️ ｜ 計算結果：15 + 27 = 42
```

### 06 hooks
```
  ✅ [PreToolUse] 放行：ls /not_exist_dir; echo done
  ⚠️  [PostToolUse] 偵測到錯誤輸出，提示模型換個作法
```

### 07 external_mcp 🔧
```
Claude: 用 fs 工具來讀取它的開頭幾行：
Claude: 完美！這是 main.py 的開頭 …（成功讀到檔案內容）
```

### 08 system_prompt_model
```
=== 字串人設 ===   Claude: 遞迴就是一個函數自己呼喚自己…直到摸著基礎情況才停船！🏴‍☠️
=== preset + append ===   …**冷知識**：堆疊溢位最常見的原因就是遞迴沒設好基礎情況…
```

### 09 sessions
```
第一輪：已記住！你的幸運數字是 7。🍀
第二輪(resume)：你的幸運數字是 7！
分叉(fork)：這條支線是 42；原本那條仍是 7。
```

### 10 custom_agents 🔧
```
Claude: 我的 code-reviewer 子代理已完成对 ./main.py 的检视：
  - 自我引用逻辑问题 / 错误处理缺失 / 成本显示逻辑不清 …
```

### 11 agent_tool_scoping 🔧
```
Claude: ./main.py 的 import 清单：
  标准库：asyncio
  claude_agent_sdk：AgentDefinition, AssistantMessage, ClaudeAgentOptions, ResultMessage, TextBlock, query
```

### 12 agent_mcp_servers 🔧
```
Claude: 台北天氣：28°C，多雲 ｜ 計算結果：12 + 30 = 42
[結束] 成本 $0.0185
```

### 13 subagent_tracking 🔧
```
  ▶️  [SubagentStart] 子代理開工 (tool_use_id=3b1d2e15…)
  ⏹️  [SubagentStop] 子代理收工 (tool_use_id=23ff6056…)
[主 agent] researcher 子代理回報：這個範例在教「子代理追蹤」…
```

### 14 observability（haiku 鐵證）
```
分模型用量: {"claude-haiku-4-5-20251001": {...}, "claude-haiku-4-5": {... "costUSD": 0.086886 ...}}
總耗時 : 28498 ms ｜ Token 用量：input/output/cache 全列
```

### 15 otel_telemetry
```
Claude: 這個資料夾有 2 個檔案。
[結束] 遙測已透過 OTLP 送出，成本 $0.0074
```

### 16 context_limits 🔧
```
=== max_turns=2 ===   [結束] subtype=error_max_turns  …  [收尾例外，已接住]
=== max_budget_usd=0.001 ===   [結束] subtype=error_max_budget_usd  ⚠️ 觸發預算上限  [收尾例外，已接住]
=== 1M 超長上下文 ===   Warning: Custom betas are only available for API key users. Ignoring…  → 仍成功
```

### 17 safety_sandbox 🔧（安全修正）
```
  🛑 擋下：路徑超出沙箱 → /notes.txt
  ✅ 放行：沙箱內寫入 → …/17_safety_sandbox/sandbox/notes.txt
```
> 實測檔案落在沙箱內，沙箱外的 `/home/sk/work/notes.txt` 不存在。

### 18 filesystem_memory
```
Claude: 本專案的吉祥物是一隻叫「阿露」的水獺 🦦。
程式碼風格：繁中註解／type hint／4 空格／雙引號。
```

### 19 advanced_persistence
```
Claude: 我看到你在做 claude-agent-class 的教學專案，目前要補完第 19 課…
（對話很短，不觸發 PreCompact；session 已存進 InMemorySessionStore）
```

---

## 改動範圍

- **19 個 `main.py`**：每課加上 `model="claude-haiku-4-5"`（第 10 課子代理原本的 `model="sonnet"` 也改成 haiku）。
- **8 課另有修正**：05（隔離）、07、10、11、12、13、16、17。
- 教學的敘述/結構都保留；新增的設定都附了中文註解說明「為什麼」。
- 沒有改動任何非 `main.py` 的檔案（產出物如 `safe_output/`、`sandbox/` 都被 `.gitignore` 忽略）。
