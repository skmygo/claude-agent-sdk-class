"""
17 — 安全沙箱：把 agent 關進指定資料夾

放手讓 agent 跑 Bash / Write 很方便，但也危險。把它關進沙箱有好幾道牆，
任一道失守還有下一道（縱深防禦）：

  cwd               工作目錄 —— agent 的「家」
  add_dirs          額外允許存取的目錄（沒列到的一律在工作範圍外）
  disallowed_tools  封死高風險工具（例如完全禁止 Bash）（snake_case！）
  permission_mode   全域權限策略
  can_use_tool      最後一道：執行時逐一審查路徑（第 04 課）
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolPermissionContext,
    query,
)

# 沙箱根目錄：agent 只能在這裡面活動
SANDBOX = Path("./sandbox").resolve()


async def confine_to_sandbox(tool_name, tool_input, context: ToolPermissionContext):
    """最後一道牆：任何想寫到沙箱外的操作都擋掉。"""
    if tool_name in {"Write", "Edit"}:
        target = Path(tool_input.get("file_path", "")).resolve()
        if not str(target).startswith(str(SANDBOX)):
            return PermissionResultDeny(message=f"路徑超出沙箱：{target}")
    return PermissionResultAllow()


async def main():
    SANDBOX.mkdir(exist_ok=True)

    options = ClaudeAgentOptions(
        cwd=str(SANDBOX),                  # 1) 把「家」設在沙箱
        allowed_tools=["Read", "Write", "Glob"],
        disallowed_tools=["Bash"],         # 2) 完全禁止跑 shell（snake_case！）
        permission_mode="default",         # 3) 標準把關，讓 can_use_tool 生效
        can_use_tool=confine_to_sandbox,   # 4) 執行時逐一審查路徑
    )

    async for message in query(
        prompt="在目前資料夾建立 notes.txt，內容寫 'hello sandbox'。",
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
