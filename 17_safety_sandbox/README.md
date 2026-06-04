# 17 — 安全沙箱：把 agent 關進指定資料夾

## 觀念

能跑 `Bash`、能 `Write` 的 agent 很強，但也意味著它「理論上」能 `rm -rf ~`、能讀你的 SSH 私鑰。生產環境必須假設「prompt 可能被注入惡意指令」，所以要把 agent 關進沙箱。

關鍵思維是**縱深防禦**——疊好幾道獨立的牆，任何一道失守，還有下一道：

```
第 1 道  cwd               把家設在沙箱目錄
第 2 道  add_dirs          只開放必要的額外目錄
第 3 道  disallowed_tools  封死高風險工具（如 Bash）
第 4 道  permission_mode   全域權限策略
第 5 道  can_use_tool      執行時逐一審查每個路徑（第 04 課）
```

## 五道牆速查

| 機制 | 擋什麼 | 層級 |
|------|--------|------|
| `cwd` | 把工作根目錄定在沙箱 | 結構 |
| `add_dirs` | 白名單外的目錄碰不到 | 結構 |
| `disallowed_tools` | 整類工具直接拿掉 | 結構 |
| `permission_mode` | 全域放寬/收緊 | 策略 |
| `can_use_tool` | 看實際參數臨場決定 | 執行時 |

> `disallowed_tools` 是 `ClaudeAgentOptions` 的欄位，**snake_case**；別和 `AgentDefinition.disallowedTools`（camelCase，第 11 課）搞混。

## 範例的雙重保險

`main.py` 同時用了「結構牆」和「執行牆」：

- **結構**：`disallowed_tools=["Bash"]` 讓 agent 根本沒有 shell 可用。
- **執行**：`can_use_tool` 把每個 `Write`/`Edit` 的目標路徑 `resolve()` 後，比對是否落在 `SANDBOX` 內——用絕對路徑比對，防住 `../../etc/passwd` 這類穿越。

## 更強的隔離：`sandbox` 選項

應用層的牆擋的是「邏輯」。要更硬的隔離，`ClaudeAgentOptions` 還有 `sandbox`（`SandboxSettings`），可走作業系統層級的沙箱。處理完全不可信的輸入時，疊加 OS 沙箱最保險。

## 重要觀念

- **永遠用絕對路徑比對**：`Path(...).resolve()` 之後再比，否則相對路徑與 `..` 會繞過你的檢查。
- **最小權限是地基**：能用 `disallowed_tools` 直接拿掉的，就別只靠執行時判斷——少一個能力，就少一條攻擊路徑。
- **沙箱 + 限制是一對**：第 16 課防「跑到失控」、第 17 課防「動到不該動的」，兩者一起才算把 agent 真正圈好。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

會在 `./sandbox/` 內建立 `notes.txt`；若 Claude 嘗試寫到沙箱外，`can_use_tool` 會擋下。
