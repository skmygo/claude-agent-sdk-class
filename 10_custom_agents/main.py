"""
10 — 自訂子代理：把任務委派給專職角色

AgentDefinition 讓你定義「子代理」——各有自己的人設、工具、模型的小幫手。
主 agent 在需要時，透過內建的 Agent 工具把子任務「外包」給它們，
子代理做完再把結果回報。這就是多代理協作的基礎。

關鍵：要在 allowed_tools 放行 "Agent"，主 agent 才叫得動子代理。
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
            "code-reviewer": AgentDefinition(
                description="審查程式碼品質與安全性的專家。需要 review 程式時叫它。",
                prompt="你是資深 code reviewer。找出 bug、效能與安全問題，給具體可行的建議。",
                tools=["Read", "Grep", "Glob"],   # 只給唯讀工具：reviewer 不該改檔
                model="claude-haiku-4-5",
            ),
            "doc-writer": AgentDefinition(
                description="撰寫技術文件的專家。需要寫 README / docstring 時叫它。",
                prompt="你是技術文件專家，文字清楚、善用範例。",
                tools=["Read", "Write", "Edit"],
                model="claude-haiku-4-5",
            ),
        },
        # 主 agent 自己的工具 + Agent（沒有 Agent 就無法委派）
        allowed_tools=["Read", "Grep", "Glob", "Agent"],
        setting_sources=[],   # 跑成範例：不吃使用者全域設定 / 上層 CLAUDE.md
    )

    async for message in query(
        prompt="用 code-reviewer 子代理檢視目前資料夾的 main.py（就在 ./main.py），直接開始、不要反問路徑，回報你發現的問題。",
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
