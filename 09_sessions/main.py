"""
09 — Session 持久化：斷點續談、分叉探索

query() 預設每次都是「全新的對話」。要延續上下文，靠 session：

  1. 第一輪從 SystemMessage(init) 抓 session_id
  2. 之後用 resume=session_id 接回去 —— Claude 記得先前讀過/說過什麼
  3. fork_session=True 從某 session「分叉」出新支線，不污染原本的

另一個快捷選項 continue_conversation=True 則是「接續最近一次對話」，
不需要自己記 session_id（適合 CLI 連續操作）。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    SystemMessage,
    TextBlock,
    query,
)


def print_text(message) -> None:
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                print(f"Claude: {block.text}")


async def main():
    session_id = None

    # --- 第一輪：建立記憶點，順手抓 session_id ---
    print("=== 第一輪：埋一個記憶點 ===")
    async for message in query(
        prompt="我的幸運數字是 7，請記住它。",
        options=ClaudeAgentOptions(max_turns=1),
    ):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            session_id = message.data["session_id"]   # ← 關鍵：開場那則就有
        print_text(message)

    print(f"\n（拿到 session_id：{session_id[:8]}…）")

    # --- 第二輪：resume 接回去，測它還記不記得 ---
    print("\n=== 第二輪：resume 續談 ===")
    async for message in query(
        prompt="我的幸運數字是多少？",
        options=ClaudeAgentOptions(resume=session_id, max_turns=1),
    ):
        print_text(message)

    # --- 分叉：從同一個 session 長出新支線，原 session 不受影響 ---
    print("\n=== 分叉：fork_session 開一條平行支線 ===")
    async for message in query(
        prompt="在這條支線把幸運數字改成 42，原本那條不要動。",
        options=ClaudeAgentOptions(resume=session_id, fork_session=True, max_turns=1),
    ):
        print_text(message)


if __name__ == "__main__":
    asyncio.run(main())
