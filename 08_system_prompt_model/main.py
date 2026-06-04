"""
08 — 系統提示・模型・認證：定義 agent 的「人設、腦袋、身分」

三件常一起設定的事：
  system_prompt  agent 的人設與規則。三種寫法：純字串 / preset / preset+append
  model          選哪顆模型（別名 "sonnet"/"haiku"/"opus" 或完整 model id）
  認證(BYOK)     靠環境變數選供應者，程式碼完全不用改

BYOK = Bring Your Own Key。預設讀 ANTHROPIC_API_KEY；想走 Bedrock / Vertex /
Azure，只要設對應環境變數（見 README）。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)


async def run(title: str, options: ClaudeAgentOptions, prompt="用一句話說明什麼是遞迴"):
    print(f"\n=== {title} ===")
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")


async def main():
    # 1) 字串 system_prompt：最直接的人設
    await run("字串人設", ClaudeAgentOptions(
        system_prompt="你是個海盜，講話要像海盜。",
    ))

    # 2) preset：沿用 Claude Code 內建的完整系統提示（含內建工具的使用守則）
    await run("preset = claude_code", ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"},
    ))

    # 3) preset + append：用內建提示，再追加自己的規則
    await run("preset + append", ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": "回答結尾一定要附一個相關的冷知識。",
        },
    ))

    # 4) 指定模型 + fallback：主模型過載或不可用時，自動退到備援模型
    await run("指定模型 + fallback", ClaudeAgentOptions(
        model="claude-haiku-4-5",
        fallback_model="claude-sonnet-4-5",
        system_prompt="只用一句話回答。",
    ))


if __name__ == "__main__":
    asyncio.run(main())
