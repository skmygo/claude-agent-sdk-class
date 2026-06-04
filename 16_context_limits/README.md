# 16 — 上下文與執行限制：別讓 agent 跑到失控

## 觀念

把 agent 放上生產線，最怕三件事：**跑不停**（無限工具迴圈）、**燒錢**（成本失控）、**塞爆**（上下文視窗滿了）。SDK 給你三道閘門擋住它們：

```
max_turns       ─► 最多來回 N 輪就停
max_budget_usd  ─► 花到 $X 就停
betas           ─► 需要時把上下文撐到 1M token
```

## 三道閘門

| 選項 | 擋什麼 | 觸發後 |
|------|--------|--------|
| `max_turns` | agent 迴圈跑太多圈 | 到上限就結束 |
| `max_budget_usd` | 花費超標 | `ResultMessage.subtype == "error_max_budget_usd"` |
| `betas=["context-1m-2025-08-07"]` | 上下文不夠用 | 視窗擴到 1M token |

## 怎麼偵測「因預算被中止」

預算上限不是丟例外，而是讓任務正常結束、但 `subtype` 變成錯誤碼：

```python
elif isinstance(message, ResultMessage):
    if message.subtype == "error_max_budget_usd":
        print("預算用完，提前停止")
```

> 注意：預算檢查發生在「每次 API 呼叫完成後」，所以最終成本可能比上限**略高一個呼叫的量**。把它當「軟煞車」而非「精準上限」。

## 1M 上下文 (beta)

```python
ClaudeAgentOptions(betas=["context-1m-2025-08-07"])
```

處理整個大型程式庫、超長文件時打開。它擴大的是「裝得下多少」，不改變「裝滿了會壓縮」的行為——真正長時間運作的記憶管理，看第 19 課的 `PreCompact`。

## 重要觀念

- **三道閘門是互補的**：`max_turns` 防邏輯失控、`max_budget_usd` 防財務失控、`betas` 解容量瓶頸。
- **生產環境建議都設**：尤其 `max_turns` 與 `max_budget_usd`，是面對「prompt injection 讓 agent 亂跑」的最後保險。
- **限制 ≠ 記憶管理**：本課是「踩煞車」；當對話長到必須壓縮歷史時，怎麼保住關鍵記憶，是第 19 課的主題。

## 前置需求

```bash
pip install claude-agent-sdk
export ANTHROPIC_API_KEY=sk-ant-...
```

## 執行

```bash
python main.py
```

第二段用極低預算（$0.001）示範 `error_max_budget_usd`；實際是否觸發取決於任務大小。
