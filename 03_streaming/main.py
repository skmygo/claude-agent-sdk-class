"""
03 — 即時串流：逐 token 顯示 Claude 的回答

預設情況下，query() 是「整段講完才給你一則 AssistantMessage」。
打開 include_partial_messages=True 後，會「額外」收到一串 StreamEvent，
裡面是模型邊想邊吐的增量片段，串起來就是打字機效果。

用途：即時 UI、邊生成邊顯示、長回答不必空等。
"""

import asyncio

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ResultMessage,
    StreamEvent,
    query,
)


def text_delta(event: dict) -> str:
    """從一個原始 streaming event 取出這次新增的文字片段（沒有就回空字串）。

    StreamEvent.event 是 Anthropic 串流協定的原始事件 dict，文字增量長這樣：
        {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Py"}}
    """
    if event.get("type") == "content_block_delta":
        delta = event.get("delta", {})
        if delta.get("type") == "text_delta":
            return delta.get("text", "")
    return ""


async def main():
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        include_partial_messages=True,  # ← 關鍵開關：打開後才會收到 StreamEvent
        max_turns=1,
    )

    print("Claude: ", end="", flush=True)

    async for message in query(
        prompt="用三句話介紹 Python 的設計哲學",
        options=options,
    ):
        # StreamEvent：逐 token 的增量，即時印出就是打字機效果
        if isinstance(message, StreamEvent):
            chunk = text_delta(message.event)
            if chunk:
                print(chunk, end="", flush=True)

        # 串流結束後仍會收到完整的 AssistantMessage（此處略過），最後是 ResultMessage
        elif isinstance(message, ResultMessage):
            print()  # 收尾換行


if __name__ == "__main__":
    asyncio.run(main())
