"""
19 — 進階持久化與壓縮：管好 agent 的長期記憶

長時間運作的 agent 有兩個進階問題，這課各給一招：

  1) 上下文快滿時，SDK 會自動「壓縮(compact)」歷史——把舊對話濃縮成摘要。
     怎麼確保關鍵資訊不被壓掉？
        → PreCompact hook：在壓縮前注入「務必保留 X」的指示

  2) 預設 session 存本機 JSONL。要多機部署、要查詢、要備援怎麼辦？
        → session_store：換成自訂後端
           本課用內建的 InMemorySessionStore 示範「形狀」；
           生產環境換成 Redis / Postgres / S3（見官方 examples/session_stores）

這兩招讓 agent 的記憶「不丟、可控、可搬」。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    InMemorySessionStore,
    ResultMessage,
    TextBlock,
    query,
)


async def protect_on_compact(input_data, tool_use_id, context):
    """PreCompact：上下文壓縮前觸發，注入指示保護關鍵記憶。

    短對話不會觸發（不需要壓縮）；對話長到逼近上限時才會進這裡。
    trigger 為 "auto"（SDK 自動）或 "manual"（使用者下 /compact）。
    """
    trigger = input_data.get("trigger", "auto")
    print(f"  🗜️  [PreCompact] 即將壓縮歷史 (trigger={trigger})，注入保護指示")
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreCompact",
            "additionalContext": (
                "壓縮摘要時，務必完整保留：使用者的需求清單、已拍板的關鍵決定、未完成的待辦事項。"
            ),
        }
    }


async def main():
    # 換掉預設的 JSONL 後端。InMemorySessionStore 是 SDK 內建的記憶體版，
    # 適合示範與測試；要持久化請換成官方參考的 Redis / Postgres / S3 adapter。
    store = InMemorySessionStore()

    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Glob"],
        session_store=store,                       # 自訂 session 持久化後端
        hooks={
            "PreCompact": [HookMatcher(hooks=[protect_on_compact])],
        },
    )

    async for message in query(
        prompt="記住：我在做一個叫 claude-agent-class 的教學專案，目前待辦是補完第 19 課。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"[結束] 成本 ${message.total_cost_usd or 0:.4f}")
            print("（這次對話很短，不會觸發 PreCompact；長對話逼近上下文上限時才會看到壓縮攔截）")


if __name__ == "__main__":
    asyncio.run(main())
