"""
15 — OpenTelemetry 遙測：把指標送進可觀測性平台

第 14 課是「每次任務結束後自己讀 ResultMessage」。要做組織級的長期監控——
跨成千上萬次執行的成本、工具使用、活躍使用者——就接 OpenTelemetry (OTel)。

Claude Code 內建 OTel 匯出，只要設好環境變數即可：metrics 走 metric 協定、
events 走 logs 協定。在 SDK 裡用 ClaudeAgentOptions(env=...) 把這些變數
注入底層 CLI 子程序，資料就會送到你的 OTLP 端點，
再轉進 Langfuse / Grafana / Datadog / Honeycomb… 任何相容後端。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

# 用環境變數打開 Claude Code 內建的 OpenTelemetry 匯出
OTEL_ENV = {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",        # 總開關
    "OTEL_METRICS_EXPORTER": "otlp",            # otlp / prometheus / console / none
    "OTEL_LOGS_EXPORTER": "otlp",               # otlp / console / none
    "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",      # grpc / http/protobuf
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
    # 需要驗證時補上：
    # "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer <token>",
    # 除錯時把匯出間隔調短（預設 metrics 60s / logs 5s）：
    "OTEL_METRIC_EXPORT_INTERVAL": "10000",     # 10 秒
}


async def main():
    # 提示：手邊沒有 OTLP collector 想先看效果？
    # 把 OTEL_METRICS_EXPORTER / OTEL_LOGS_EXPORTER 改成 "console"，指標會直接印到終端機。
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        env=OTEL_ENV,                 # ← 關鍵：用 env 把遙測設定注入子程序
        allowed_tools=["Read", "Glob"],
    )

    async for message in query(
        prompt="列出這個資料夾的檔案數量。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"\n[結束] 遙測已透過 OTLP 送出，成本 ${message.total_cost_usd or 0:.4f}")
            print("（若把 exporter 設成 console，上方會看到 OTel 指標輸出）")


if __name__ == "__main__":
    asyncio.run(main())
