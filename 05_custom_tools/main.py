"""
05 — 自訂工具：把 Python 函式變成 Claude 的工具

兩個關鍵 API：
  @tool(...)                 把一個 async 函式標記成工具
  create_sdk_mcp_server(...) 把多個工具打包成「進程內 MCP 伺服器」
                             —— 不必另開程序，直接在你的 Python 行程裡跑

命名規則（很重要）：掛載後工具全名是 mcp__<伺服器名>__<工具名>，
要在 allowed_tools 裡用這個全名預先放行，否則每次呼叫都會卡權限。
"""

import asyncio
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)


# --- 用 @tool 定義工具 ---
# 簽名：@tool(名稱, 給模型看的說明, 參數 schema)
# 參數 schema 用 {"欄位名": 型別} 的簡寫即可，SDK 會轉成 JSON Schema 給模型看。
@tool("get_weather", "查詢某城市目前天氣（示範用假資料）", {"city": str})
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    fake = {"台北": "28°C 多雲", "東京": "22°C 晴", "倫敦": "12°C 小雨"}
    city = args["city"]
    text = fake.get(city, f"查無「{city}」的天氣資料")
    print(f"  [工具被呼叫] get_weather(city={city!r}) → {text}")
    # 回傳格式固定：content 是一串內容區塊
    return {"content": [{"type": "text", "text": text}]}


@tool("add", "把兩個數字相加", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    total = args["a"] + args["b"]
    print(f"  [工具被呼叫] add({args['a']}, {args['b']}) → {total}")
    return {"content": [{"type": "text", "text": f"{args['a']} + {args['b']} = {total}"}]}


async def main():
    # 把工具打包成進程內 MCP 伺服器
    toolbox = create_sdk_mcp_server(
        name="toolbox",
        version="1.0.0",
        tools=[get_weather, add],
    )

    options = ClaudeAgentOptions(
        model="claude-haiku-4-5",
        mcp_servers={"toolbox": toolbox},   # "toolbox" 是掛載名 → 影響工具全名
        allowed_tools=[                      # 用全名預先放行
            "mcp__toolbox__get_weather",
            "mcp__toolbox__add",
        ],
        setting_sources=[],   # 跑成範例：不吃使用者全域設定（避免一堆外部 MCP 工具干擾選用）
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query("台北現在天氣如何？順便幫我算 15 + 27")
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")
            elif isinstance(message, ResultMessage):
                print(f"[結束] 成本 ${message.total_cost_usd or 0:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
