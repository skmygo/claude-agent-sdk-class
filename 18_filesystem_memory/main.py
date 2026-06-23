"""
18 — 檔案系統設定與記憶：CLAUDE.md、commands、agents

到目前為止，設定都寫在 Python 裡。但 Claude Code 也能從檔案系統載入設定，
這是「跨 session 記憶」最自然的做法：把專案知識寫進 CLAUDE.md，
agent 每次啟動都自動讀到，不必每次在 prompt 裡重講。

setting_sources 控制要載入哪些來源：
  "user"     ~/.claude/             全域使用者設定
  "project"  .claude/ + CLAUDE.md   專案層級（最常用）
  "local"    本機 gitignore 的設定

可載入：CLAUDE.md（記憶）、.claude/commands/（slash 指令）、
.claude/agents/（子代理）、.claude/skills/（技能）。

本課資料夾放了一個 CLAUDE.md，跑起來 Claude 會「記得」裡面寫的事。
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    SystemMessage,
    TextBlock,
    query,
)

HERE = Path(__file__).parent


async def main():
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        cwd=str(HERE),
        # None（不設）= 載入全部預設來源；[] = 完全不載入；這裡只載入專案層級
        setting_sources=["project"],
        max_turns=1,
    )

    async for message in query(
        prompt="這個專案的吉祥物是誰？我們的程式碼風格規則有哪些？",
        options=options,
    ):
        # init 訊息會列出從檔案系統載入了哪些 commands / agents
        if isinstance(message, SystemMessage) and message.subtype == "init":
            print(f"載入的 slash commands：{message.data.get('slash_commands', [])}")
            print(f"載入的 agents：{message.data.get('agents', [])}\n")
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")


if __name__ == "__main__":
    asyncio.run(main())
