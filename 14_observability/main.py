"""
14 — 成本與用量：把每一次執行量化

要把 agent 放上生產線，先得能回答：花了多少錢？用了多少 token？跑了幾輪？
這些 SDK 都幫你算好，放在 ResultMessage 裡：

  total_cost_usd  這次任務的總花費（USD）
  usage           token 用量（input / output / cache 讀寫…）
  num_turns       來回了幾輪
  duration_ms     總耗時（毫秒）
  model_usage     分模型的用量（用到子代理 / fallback 時特別有用）

外加 stderr callback，可攔截底層 CLI 的警告與除錯輸出。
"""

import asyncio
import json

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


def stderr_logger(line: str) -> None:
    """底層 CLI 的每一行 stderr 都會進這裡（警告、除錯訊息…）。"""
    if "[ERROR]" in line or "warn" in line.lower():
        print(f"  [stderr] {line}")


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        stderr=stderr_logger,   # 攔截 CLI 的 stderr
    )

    async for message in query(
        prompt="這個資料夾裡有幾個 .md 檔？挑一個讀來摘要一下。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")

        elif isinstance(message, ResultMessage):
            # 任務收尾：把可觀測性指標一次印出
            print("\n===== 執行報告 =====")
            print(f"結束狀態  : {message.subtype}")
            print(f"總花費    : ${message.total_cost_usd or 0:.6f}")
            print(f"回合數    : {message.num_turns}")
            print(f"總耗時    : {message.duration_ms} ms")
            if message.usage:
                print(f"Token 用量 : {json.dumps(message.usage, ensure_ascii=False)}")
            if message.model_usage:
                print(f"分模型用量: {json.dumps(message.model_usage, ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())
