# 12 — 子代理專屬 MCP：不同 agent 掛不同工具箱

## 觀念

第 11 課切的是內建工具的範圍。但如果你的能力來自 MCP（自訂工具、外部服務），要怎麼讓「天氣助手只有天氣工具、數學助手只有計算工具」？答案是 `AgentDefinition.mcpServers`：

```
全域定義：mcp_servers = { "weather": …, "math": … }
                 │
   weather-bot ──┴─ mcpServers=["weather"]   只看得到天氣工具
   math-bot    ──── mcpServers=["math"]      只看得到計算工具
```

## 兩步驟

```python
options = ClaudeAgentOptions(
    # 1) 全域先把 server 都定義好（進程內或外部皆可）
    mcp_servers={"weather": weather_server, "math": math_server},
    agents={
        "weather-bot": AgentDefinition(
            ...,
            mcpServers=["weather"],                 # 2) 引用全域 server 名
            tools=["mcp__weather__get_weather"],
        ),
    },
)
```

## `mcpServers` 的兩種寫法

| 寫法 | 範例 | 意思 |
|------|------|------|
| 名稱字串 | `["weather"]` | 引用 `options.mcp_servers` 裡已定義的 server |
| inline dict | `[{"name": {...config}}]` | 直接在 agent 內聯定義一個 server |

名稱字串最常用：server 集中定義一次，各 agent 各取所需。

## 為什麼要切到這麼細

- **工具污染**：工具一多，模型容易選錯。每個子代理只看到該看的，選擇更準。
- **安全邊界**：能查內部資料庫的 MCP，只給「資料分析」子代理，不給「對外回覆」子代理。
- **責任清晰**：一個 agent 一個工具箱，出問題好定位。

## 重要觀念

- **`mcpServers` 是 camelCase**（同第 10、11 課的提醒）。
- **記得同時設 `tools`**：掛了 server 還要在 `tools` 放行對應的 `mcp__<server>__<tool>`，agent 才用得到。
- **進程內、外部都能掛**：本課用第 05 課的進程內 server；換成第 07 課的外部 server（dict 設定）也一樣。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
