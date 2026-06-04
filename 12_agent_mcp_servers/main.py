"""
12 — 子代理專屬 MCP：不同 agent 掛不同工具箱

第 11 課切的是「內建工具」的範圍；這課切「MCP 工具」。
你可以讓每個子代理掛載自己專屬的 MCP 伺服器：
  天氣助手只看得到天氣工具，數學助手只看得到計算工具，互不干擾。

做法兩步：
  1. 在 options.mcp_servers 把所有 server 定義好（這裡用第 05 課的進程內 server）
  2. 用 AgentDefinition.mcpServers（camelCase）指定「這個 agent 掛哪幾個」
"""

import asyncio
from typing import Any

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
    tool,
)


@tool("get_weather", "查城市天氣（假資料）", {"city": str})
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    data = {"台北": "28°C 多雲", "東京": "22°C 晴"}
    return {"content": [{"type": "text", "text": data.get(args["city"], "查無資料")}]}


@tool("add", "兩數相加", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": str(args["a"] + args["b"])}]}


async def main():
    weather_server = create_sdk_mcp_server(name="weather", tools=[get_weather])
    math_server = create_sdk_mcp_server(name="math", tools=[add])

    options = ClaudeAgentOptions(
        # 1) 先在全域定義所有 server
        mcp_servers={"weather": weather_server, "math": math_server},
        agents={
            # 2) 天氣助手「只」掛 weather
            "weather-bot": AgentDefinition(
                description="回答天氣問題。",
                prompt="你只負責天氣，用 weather 工具查。",
                mcpServers=["weather"],                    # camelCase，引用全域 server 名
                tools=["mcp__weather__get_weather"],
            ),
            # 數學助手「只」掛 math
            "math-bot": AgentDefinition(
                description="負責算數。",
                prompt="你只負責計算，用 math 工具算。",
                mcpServers=["math"],
                tools=["mcp__math__add"],
            ),
        },
        allowed_tools=["Agent"],
    )

    async for message in query(
        prompt="叫 weather-bot 查台北天氣，再叫 math-bot 算 12 + 30。",
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
