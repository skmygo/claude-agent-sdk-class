"""
06 — 生命週期 Hooks：在關鍵時刻插入你的程式碼

Hook 是 agent 生命週期事件的回呼。常用事件：
  PreToolUse        工具「即將」執行 → 可放行 / 擋下 / 改寫
  PostToolUse       工具「剛跑完」   → 可審查輸出、補充脈絡
  UserPromptSubmit  使用者送出 prompt → 可注入額外資訊
  Stop / SubagentStart / SubagentStop / SessionStart / PreCompact ...

用 HookMatcher 把「某事件 + 某工具」綁到回呼。回呼回傳一個 dict 來控制行為
（空 dict {} 代表「不干預」）。

Hook callback 簽名固定是三個參數：(input_data, tool_use_id, context)。
這裡用 dict 型別讓它直白；input_data 內含 tool_name / tool_input / tool_response。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    TextBlock,
)


async def block_dangerous_bash(input_data, tool_use_id, context):
    """PreToolUse：Bash 指令執行前先檢查，危險就擋下。"""
    if input_data.get("tool_name") != "Bash":
        return {}  # 不是 Bash，不干預

    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        print(f"  🛑 [PreToolUse] 擋下危險指令：{command}")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",       # deny / allow / ask
                "permissionDecisionReason": "禁止 rm -rf",
            }
        }
    print(f"  ✅ [PreToolUse] 放行：{command}")
    return {}


async def review_output(input_data, tool_use_id, context):
    """PostToolUse：工具跑完後審查輸出，發現錯誤就補一句脈絡給模型。"""
    response = str(input_data.get("tool_response", "")).lower()
    if "error" in response or "no such" in response:
        print("  ⚠️  [PostToolUse] 偵測到錯誤輸出，提示模型換個作法")
        return {
            "systemMessage": "上一個指令出錯了",   # 顯示給使用者看的提示
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": "指令執行失敗，請檢查語法或換個方法。",  # 餵回給模型
            },
        }
    return {}


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"],
        hooks={
            # matcher 篩工具名，支援 regex（例如 "Edit|Write"）；matcher=None 代表全部
            "PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_dangerous_bash])],
            "PostToolUse": [HookMatcher(matcher="Bash", hooks=[review_output])],
        },
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("先用 bash 跑 `ls /not_exist_dir`，再跑 `echo done`")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"[結束] 成本 ${message.total_cost_usd or 0:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
