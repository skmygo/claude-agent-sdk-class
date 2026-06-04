# 14 — 成本與用量：把每一次執行量化

## 觀念

prototype 階段你不在乎花多少錢；上生產線就完全相反——每一次執行的成本、token、耗時都要能追。好消息是 SDK 全幫你算好了，全在最後那則 `ResultMessage` 裡。

```
任務跑完 ──► ResultMessage ──► total_cost_usd / usage / num_turns / duration_ms / model_usage
```

這課示範把這些「攤平印出來」，就是一份最基本的執行報告。

## ResultMessage 上的可觀測性欄位

| 欄位 | 意義 |
|------|------|
| `total_cost_usd` | 本次任務總花費（USD） |
| `usage` | token 明細：input / output / cache 讀寫 |
| `num_turns` | 來回幾輪（agent 迴圈跑幾圈） |
| `duration_ms` / `duration_api_ms` | 總耗時 / 純 API 耗時 |
| `model_usage` | 依模型拆分的用量（用到子代理/fallback 必看） |
| `subtype` | 結束原因（`success` / 各種 error_*） |
| `permission_denials` | 被拒絕的工具呼叫紀錄 |

## stderr callback

底層 CLI 的警告與除錯訊息走 stderr，用 callback 接住：

```python
def stderr_logger(line: str):
    if "[ERROR]" in line:
        print(line)

options = ClaudeAgentOptions(stderr=stderr_logger)
```

想要更詳盡的 debug log，可加 `extra_args={"debug-file": "/path/to/log"}` 把 CLI 詳細日誌寫到檔案再讀。

## 重要觀念

- **`total_cost_usd` 可能是 `0` 或 `None`**：用訂閱額度或某些供應者時不一定有金額，記得 `or 0` 防呆。
- **`usage` 的 cache 欄位很關鍵**：cache 命中率高 = 省錢，調 prompt 時盯著它看。
- **`model_usage` 揭露「隱形成本」**：子代理可能偷偷用了較貴的模型，分模型用量幫你抓出來。
- **這是「單次、被動」的可觀測性**：適合腳本、CI。要做組織級「跨上萬次執行」的長期監控，看下一課的 OpenTelemetry。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```
