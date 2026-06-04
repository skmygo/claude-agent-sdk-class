# 15 — OpenTelemetry 遙測：把指標送進可觀測性平台

## 觀念

第 14 課是「跑完一次、自己讀 `ResultMessage`」——適合腳本，但無法回答組織級問題：「上個月所有 agent 共花多少錢？哪個工具用最兇？哪天最忙？」

這要靠標準化的遙測管線。Claude Code **內建 OpenTelemetry (OTel)** 匯出——metrics 走指標協定、events 走 logs 協定——你只要設好環境變數，資料就會源源不絕送進你的可觀測性後端：

```
Claude Code ──OTLP──► OTel Collector ──► Langfuse / Grafana / Datadog / Honeycomb …
```

## 在 SDK 裡怎麼打開

關鍵是用 `ClaudeAgentOptions(env=...)` 把遙測環境變數注入底層 CLI 子程序：

```python
options = ClaudeAgentOptions(env={
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
})
```

## 環境變數速查

| 變數 | 作用 | 常見值 |
|------|------|--------|
| `CLAUDE_CODE_ENABLE_TELEMETRY` | 總開關 | `1` |
| `OTEL_METRICS_EXPORTER` | metrics 匯出器 | `otlp` / `prometheus` / `console` / `none` |
| `OTEL_LOGS_EXPORTER` | events 匯出器 | `otlp` / `console` / `none` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | 傳輸協定 | `grpc` / `http/protobuf` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | collector 端點 | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_HEADERS` | 驗證標頭 | `Authorization=Bearer <token>` |
| `OTEL_METRIC_EXPORT_INTERVAL` | metrics 匯出間隔(ms) | `10000`（除錯用，預設 60000） |

## 匯出哪些東西

- **Metrics（指標）**：session 數、token 用量、成本、程式碼行數變更、工具使用次數…
- **Events / Logs（事件）**：使用者 prompt、工具執行結果、API 請求、權限決策…

## 想先看效果，不想架 collector？

把匯出器設成 `console`，指標直接印在終端機：

```python
env={"CLAUDE_CODE_ENABLE_TELEMETRY": "1", "OTEL_METRICS_EXPORTER": "console", "OTEL_LOGS_EXPORTER": "console"}
```

## 重要觀念

- **14 vs 15 是「戰術 vs 戰略」**：14 課的 `ResultMessage` 是單次、即時、程式可讀；15 課的 OTel 是長期、聚合、平台可視化。生產環境兩者都要。
- **遙測設定走 `env`，不是寫死的選項**：這也示範了 `env` 參數的威力——任何 Claude Code 支援的環境變數（含第 08 課的 BYOK 變數）都能這樣針對單一 agent 注入。
- **間隔記得改回預設**：`OTEL_METRIC_EXPORT_INTERVAL` 調短只適合除錯，生產環境別讓它狂送。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
# 要真的收到資料，需有 OTLP collector（如 OpenTelemetry Collector）監聽 4317
# 只想試跑：把 exporter 改成 console 即可，免 collector
```

## 執行

```bash
python main.py
```

詳細的指標/事件清單見官方文件：<https://code.claude.com/docs/zh-TW/monitoring-usage>
