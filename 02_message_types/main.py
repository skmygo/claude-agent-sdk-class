"""
02 — 訊息型別：讀懂 Agent 吐出的訊息流

query() / client 會吐出一串訊息，看懂每一種，你才知道 agent 在幹嘛：

  SystemMessage    開場白：session_id、可用工具、模型… （subtype == "init"）
  AssistantMessage Claude 的發言：TextBlock（說話）或 ToolUseBlock（要用工具）
  UserMessage      工具執行結果會以 user 角色「回填」：ToolResultBlock
  ResultMessage    收尾：成本、回合數、最終結果字串

這一課故意給一個「需要動用工具」的任務，才能看到完整的訊息流。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)


def show(message) -> None:
    """把每一種訊息印成人看得懂的格式。"""

    # 1) 開場：只有第一則 SystemMessage 的 subtype 是 "init"
    if isinstance(message, SystemMessage):
        if message.subtype == "init":
            session_id = message.data.get("session_id", "")
            tools = message.data.get("tools", [])
            print(f"[system/init] session={session_id[:8]}…  可用工具 {len(tools)} 個")

    # 2) Claude 的發言：content 可能同時混著「說話」與「呼叫工具」
    elif isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"[assistant/text] {block.text.strip()}")
            elif isinstance(block, ToolUseBlock):
                print(f"[assistant/tool_use] 呼叫 {block.name}，輸入={block.input}")

    # 3) 工具結果：SDK 用 user 角色把結果回填給模型
    elif isinstance(message, UserMessage):
        if isinstance(message.content, list):
            for block in message.content:
                if isinstance(block, ToolResultBlock):
                    preview = str(block.content)[:80].replace("\n", " ")
                    print(f"[user/tool_result] {preview}…")

    # 4) 收尾：拿成本、回合數、最終結果
    elif isinstance(message, ResultMessage):
        print(f"[result] subtype={message.subtype}  "
              f"成本 ${message.total_cost_usd or 0:.4f}  回合 {message.num_turns}")
        if message.result:
            print(f"[result/text] {message.result.strip()}")


async def main():
    # 開放 Bash 工具，Claude 才會真的去呼叫工具，我們也才看得到 tool_use / tool_result
    options = ClaudeAgentOptions(allowed_tools=["Bash"])

    async for message in query(
        prompt="用一行 bash 指令印出今天的日期，然後告訴我結果",
        options=options,
    ):
        show(message)


if __name__ == "__main__":
    asyncio.run(main())
