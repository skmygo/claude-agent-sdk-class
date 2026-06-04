"""
04 — 權限控制：用 can_use_tool 動態守門

agent 要動手（寫檔、跑指令）前，SDK 會先問你的 can_use_tool callback：
「這個工具、這組輸入，准不准？」你有三種回答：
  - 放行         → PermissionResultAllow()
  - 改寫後放行   → PermissionResultAllow(updated_input=改過的輸入)
  - 擋下         → PermissionResultDeny(message="理由")

這比 allowed_tools 的「靜態白名單」更靈活：你能看著「實際參數」臨場決定。
"""

import asyncio

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolPermissionContext,
)

READONLY = {"Read", "Glob", "Grep"}
DANGEROUS = ["rm -rf", "sudo", "mkfs", "dd if=", ":(){"]


async def gatekeeper(
    tool_name: str,
    tool_input: dict,
    context: ToolPermissionContext,
) -> PermissionResultAllow | PermissionResultDeny:
    """每次工具呼叫前都會進這裡，回傳 Allow / Deny 決定放不放行。"""
    print(f"\n🛂 申請使用 {tool_name}：{tool_input}")

    # 1) 唯讀工具一律放行
    if tool_name in READONLY:
        print("   ✅ 唯讀，直接放行")
        return PermissionResultAllow()

    # 2) Bash：擋下危險指令，其餘放行
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        for bad in DANGEROUS:
            if bad in command:
                print(f"   ❌ 偵測到危險樣式：{bad}")
                return PermissionResultDeny(message=f"禁止危險指令：{bad}")
        print("   ✅ 指令安全，放行")
        return PermissionResultAllow()

    # 3) 寫檔：改寫路徑，強制塞進 ./safe_output/（示範 updated_input）
    if tool_name in {"Write", "Edit"}:
        path = tool_input.get("file_path", "")
        if not path.startswith("./safe_output/"):
            safe = f"./safe_output/{path.split('/')[-1]}"
            print(f"   ⚠️  把寫入路徑從 {path} 改寫成 {safe}")
            return PermissionResultAllow(updated_input={**tool_input, "file_path": safe})
        return PermissionResultAllow()

    # 4) 其他工具：保守拒絕
    print("   ❓ 未知工具，保守拒絕")
    return PermissionResultDeny(message=f"未授權的工具：{tool_name}")


async def main():
    options = ClaudeAgentOptions(
        can_use_tool=gatekeeper,
        permission_mode="default",  # 必須用 default，callback 才會被呼叫
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "請依序做：1) 列出目前資料夾的檔案 2) 把 'hello' 寫進 note.txt"
        )
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"\nClaude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"\n[結束] 成本 ${message.total_cost_usd or 0:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
