"""
07 — 外部 MCP 伺服器：接上整個工具生態系

第 05 課的工具跑在你的 Python 行程裡；這課要連「別人寫好、跑在另一個程序」
的 MCP 伺服器。設定方式都是 mcp_servers，差別只在傳輸型態：

  stdio  本地子程序（最常見，用 npx / uvx 啟動）
  http   遠端 HTTP 伺服器
  sse    遠端 SSE 伺服器

掛上去後，工具一樣是 mcp__<伺服器名>__<工具名>，用全名放行。
本例用官方的 filesystem MCP，把它限定在目前資料夾。
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
    options = ClaudeAgentOptions(
        mcp_servers={
            # stdio：npx 啟動官方 filesystem MCP，最後的 "." 限定它只能碰目前資料夾
            "fs": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
            },
            # http：連遠端 MCP（示意，註解掉。換成你自己的端點即可）
            # "remote": {
            #     "type": "http",
            #     "url": "https://example.com/mcp",
            #     "headers": {"Authorization": "Bearer <token>"},
            # },
        },
        allowed_tools=[
            "mcp__fs__list_directory",
            "mcp__fs__read_file",
        ],
        max_turns=3,
    )

    async for message in query(
        prompt="用 fs 工具列出目前資料夾，挑一個 .py 檔讀出開頭幾行給我看",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"[結束] 成本 ${message.total_cost_usd or 0:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
