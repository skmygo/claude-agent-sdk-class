"""
11 — 子代理工具範圍：每個 agent 各管各的權限

第 10 課每個子代理都設了 tools，這課把焦點放在「範圍控制」本身：
  tools            白名單：這個 agent「只能」用這些
  disallowedTools  黑名單：明確禁止某些工具（注意 camelCase！）

原則是「最小權限」：reviewer 不該能改檔、分析員不該能跑指令。
把權限切乾淨，agent 就算被誘導也做不出超出職權的事。
"""

import asyncio

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)


async def main():
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        agents={
            # 唯讀分析員：只能看，不能動
            "analyst": AgentDefinition(
                model="claude-haiku-4-5",
                description="分析程式碼結構與壞味道，只做唯讀分析。",
                prompt="你是程式碼分析師，只閱讀與歸納，絕不修改任何檔案。",
                tools=["Read", "Grep", "Glob"],     # 白名單只給唯讀工具
            ),
            # 編輯員：能讀寫，但明確禁止跑 shell
            "editor": AgentDefinition(
                model="claude-haiku-4-5",
                description="依指示修改檔案內容，但不執行任何指令。",
                prompt="你負責編輯檔案，不跑任何 shell 指令。",
                tools=["Read", "Write", "Edit"],
                disallowedTools=["Bash"],            # camelCase！明確禁止 Bash
            ),
        },
        allowed_tools=["Read", "Grep", "Glob", "Agent"],
        setting_sources=[],   # 跑成範例：不吃使用者全域設定 / 上層 CLAUDE.md
    )

    async for message in query(
        prompt="用 analyst 子代理分析目前資料夾的 main.py（就在 ./main.py），直接開始、不要反問路徑，列出它 import 了哪些東西。",
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
