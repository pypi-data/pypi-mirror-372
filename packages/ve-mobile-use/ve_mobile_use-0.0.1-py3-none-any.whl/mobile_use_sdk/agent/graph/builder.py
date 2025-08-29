from langgraph.graph import END, StateGraph

from mobile_use_sdk.agent.graph.nodes import (
    model_node,
    prepare_node,
    should_react_continue,
    tool_node,
)
from mobile_use_sdk.agent.graph.nodes.compact import compact_node
from mobile_use_sdk.agent.graph.nodes.screenshot import screenshot_node
from mobile_use_sdk.agent.graph.state import MobileUseAgentState
from mobile_use_sdk.agent.llm import LLM
from mobile_use_sdk.agent.memory.saver import checkpointer
from mobile_use_sdk.agent.tools import Tools
from mobile_use_sdk.mobile import Mobile


def create_mobile_use_agent(
    llm: LLM,
    mobile: Mobile | None = None,
    tools: Tools | None = None,
    additional_system_prompt: str = "",
):
    """创建代理.

    Args:
        llm: 语言模型实例，用于model_node的推理
        mobile: 移动端客户端实例
        tools: 工具集合实例
    """
    # 创建状态图
    workflow = StateGraph(MobileUseAgentState)

    workflow.add_node("prepare", prepare_node(mobile, tools, additional_system_prompt))
    workflow.set_entry_point("prepare")  # 设置入口节点

    # 添加五个核心节点
    workflow.add_node("screenshot", screenshot_node(mobile))  # 截图节点
    workflow.add_node("model", model_node(llm))  # 大模型节点，计算action和tool
    workflow.add_node("tool", tool_node(tools))  # 工具执行节点
    workflow.add_node("compact", compact_node(llm))  # 消息压缩节点

    # 设置节点之间的边
    workflow.add_edge("prepare", "screenshot")
    workflow.add_edge("screenshot", "model")
    workflow.add_edge("model", "tool")

    workflow.add_conditional_edges(
        "tool",
        should_react_continue(tools),
        {
            "continue": "compact",  # 继续下一轮，先压缩消息
            "finish": END,  # 任务完成
        },
    )

    # 添加从compact到screenshot的边
    workflow.add_edge("compact", "screenshot")

    # 编译状态图
    return workflow.compile(name="mobile_use_agent", checkpointer=checkpointer)


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    from mobile_use_sdk.agent.llm.doubao import DoubaoLLM
    from mobile_use_sdk.config import LLMConfig

    # launch.json 具体的路径
    load_dotenv(dotenv_path=os.getenv("DOTENV_PATH"))

    llm = DoubaoLLM(
        llm_config=LLMConfig(
            model=os.getenv("ARK_MODEL_ID"),
            api_key=os.getenv("ARK_API_KEY"),
            base_url=os.getenv("ARK_BASE_URL"),
        )
    )
    # print(create_mobile_use_agent(llm).get_graph().draw_mermaid())
