"""
16 — 上下文與執行限制：別讓 agent 跑到失控

長對話 / 複雜任務有幾個風險：跑太多輪、花太多錢、塞爆上下文視窗。
SDK 給你三道閘門：

  max_turns       最多來回幾輪（防無限工具迴圈）
  max_budget_usd  花費上限；超過就停，ResultMessage.subtype 變 error_max_budget_usd
  betas           開啟 1M token 超長上下文（"context-1m-2025-08-07"）
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def run(title: str, options: ClaudeAgentOptions, prompt: str):
    print(f"\n=== {title} ===")
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"[結束] subtype={message.subtype}  "
                  f"成本 ${message.total_cost_usd or 0:.4f}  回合 {message.num_turns}")
            if message.subtype == "error_max_budget_usd":
                print("⚠️  觸發預算上限，提前停止（成本可能略超，因為以「整次 API 呼叫」為單位結算）")


async def main():
    # 1) max_turns：限制來回次數，避免 agent 在工具迴圈裡打轉
    await run(
        "max_turns=2",
        ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Bash"], max_turns=2),
        "統計這個資料夾各副檔名各有幾個檔案。",
    )

    # 2) max_budget_usd：花費上限。給一個很緊的預算讓它提前觸發
    await run(
        "max_budget_usd=0.001（故意調很低）",
        ClaudeAgentOptions(allowed_tools=["Read", "Glob"], max_budget_usd=0.001),
        "逐一讀完整個資料夾每個檔案，寫一份非常詳盡的導讀。",
    )

    # 3) betas：開啟 1M token 超長上下文（處理大型程式庫 / 長文件時）
    await run(
        "1M 超長上下文",
        ClaudeAgentOptions(betas=["context-1m-2025-08-07"], max_turns=1),
        "用一句話自我介紹。",
    )


if __name__ == "__main__":
    asyncio.run(main())
