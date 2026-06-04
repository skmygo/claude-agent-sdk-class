"""
13 — 子代理追蹤：看清楚是誰在做事

多代理跑起來，所有訊息混在同一條流裡。怎麼分辨「這句是主 agent 還是子代理說的」？
兩個工具：

  parent_tool_use_id  訊息上的欄位。None = 主 agent 說的；
                      有值 = 某個子代理說的（值就是發起它的那次 Agent 呼叫 id）
  SubagentStart/Stop  hooks 事件，標記子代理的「開工」與「收工」

把這兩者結合，就能還原「主 → 子」的活動軌跡，做日誌或即時 UI。
"""

import asyncio

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    query,
)


async def on_subagent_start(input_data, tool_use_id, context):
    print(f"  ▶️  [SubagentStart] 子代理開工 (tool_use_id={tool_use_id})")
    return {}


async def on_subagent_stop(input_data, tool_use_id, context):
    print(f"  ⏹️  [SubagentStop] 子代理收工 (tool_use_id={tool_use_id})")
    return {}


def who(message) -> str:
    """靠 parent_tool_use_id 分辨發話者。"""
    pid = getattr(message, "parent_tool_use_id", None)
    return "主 agent" if pid is None else f"子代理({pid[:8]}…)"


async def main():
    options = ClaudeAgentOptions(
        agents={
            "researcher": AgentDefinition(
                description="調查並摘要某個主題。",
                prompt="你是研究員，簡潔摘要重點。",
                tools=["Read", "Grep", "Glob"],
            ),
        },
        allowed_tools=["Read", "Grep", "Glob", "Agent"],
        hooks={
            # 非工具事件，matcher 省略（= None，不篩）
            "SubagentStart": [HookMatcher(hooks=[on_subagent_start])],
            "SubagentStop": [HookMatcher(hooks=[on_subagent_stop])],
        },
    )

    async for message in query(
        prompt="叫 researcher 子代理看看這個資料夾在教什麼，回報主題。",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # 在每句話前標出「是誰說的」
                    print(f"[{who(message)}] {block.text}")
        elif isinstance(message, ResultMessage):
            print(f"[結束] 成本 ${message.total_cost_usd or 0:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
