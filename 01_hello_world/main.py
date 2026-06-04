"""
01 — Hello World：Claude Agent SDK 最小可運行範例

最小流程：query() 送一句話 → 非同步迭代它吐出的訊息 → 取出文字與成本。
這是整個 SDK 最基礎的形狀，後面每一課都是在這上面加東西。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    # query() 回傳一個 async 迭代器：對話過程中的每一則訊息都會被「吐」出來。
    # options 可省略（連 system_prompt 都不給也能跑）；這裡示範兩個常用選項。
    options = ClaudeAgentOptions(
        system_prompt="You are a helpful assistant. Answer in one sentence.",
        max_turns=1,  # 這題不需要工具，限制 1 輪避免多餘往返
    )

    async for message in query(prompt="What is 2 + 2?", options=options):
        # AssistantMessage = Claude 的發言；content 是一串「內容區塊」
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")

        # ResultMessage = 任務收尾的總結（成本、回合數、最終結果…）
        elif isinstance(message, ResultMessage):
            if message.total_cost_usd:
                print(f"\n花費 ${message.total_cost_usd:.4f}，共 {message.num_turns} 回合")


if __name__ == "__main__":
    asyncio.run(main())
