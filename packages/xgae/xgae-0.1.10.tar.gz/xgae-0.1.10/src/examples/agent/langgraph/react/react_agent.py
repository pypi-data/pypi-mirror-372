import asyncio
import logging
from typing import Any, Dict, List, Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from xgae.engine.engine_base import XGATaskResult, XGAResponseMessage
from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.utils.setup_env import setup_langfuse, setup_logging
from xgae.utils import handle_error
from xgae.utils.misc import read_file

class TaskState(TypedDict, total=False):
    """State definition for the agent orchestration graph"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_input: str
    next_node: str
    context: Dict[str, Any]
    system_prompt: str
    custom_tools: List[str]
    general_tools: List[str]
    task_result: XGATaskResult
    formatted_result: XGATaskResult
    iteration_count: int

langfuse = setup_langfuse()

class XGAReactAgent:
    MAX_TASK_RETRY = 2
    def __init__(self):
        self.tool_box = XGAMcpToolBox()

    async def _create_graph(self) -> StateGraph:
        try:
            graph_builder = StateGraph(TaskState)

            # Add nodes
            graph_builder.add_node("supervisor", self._supervisor_node)
            graph_builder.add_node("select_tool", self._select_tool_node)
            graph_builder.add_node("exec_task", self._exec_task_node)
            graph_builder.add_node("eval_result", self._eval_result_node)
            graph_builder.add_node("format_result", self._format_result_node)

            # Add edges
            graph_builder.add_edge(START, "supervisor")
            graph_builder.add_conditional_edges(
                "supervisor",
                self._next_condition,
                {
                    "select_tool": "select_tool",
                    "exec_task": "exec_task",
                    "format_result": "format_result"
                }
            )

            graph_builder.add_edge("select_tool", "exec_task")
            graph_builder.add_edge("exec_task", "eval_result")

            graph_builder.add_conditional_edges(
                "eval_result",
                self._next_condition,
                {
                    "retry": "supervisor",
                    "format_result": "format_result",
                }
            )
            
            graph_builder.add_edge("format_result", END)
            
            graph = graph_builder.compile(checkpointer=MemorySaver())
            graph.name = "XGARectAgent"

            return graph
        except Exception as e:
            logging.error("Failed to create XGARectAgent graph: %s", str(e))
            raise


    async def _supervisor_node(self, state: TaskState) -> Dict[str, Any]:
        user_input = state.get("user_input", "")
        system_prompt = None if "fault" in user_input else read_file("templates/example/fault_user_prompt.txt")
        return {
            "system_prompt" : system_prompt,
            "next_node" : "select_tool",
        }

    async def _select_tool_node(self, state: TaskState) -> Dict[str, Any]:
        system_prompt = state.get("system_prompt",None)
        general_tools = ["*"] if system_prompt else []
        custom_tools = ["*"] if not system_prompt  else []
        return {
            "general_tools" : general_tools,
            "custom_tools" : custom_tools,
        }

    async def _exec_task_node(self, state: TaskState) -> Dict[str, Any]:
        task_result = XGATaskResult(type="answer", content="test task result")
        return {
            "task_result" : task_result
        }

    async def _eval_result_node(self, state: TaskState) -> Dict[str, Any]:
        next_node = "end"
        return {
            "next_node" : next_node
        }

    async def _format_result_node(self, state: TaskState) -> Dict[str, Any]:
        formatted_result = state.get("task_result")
        return {
            "formatted_result" : formatted_result,
            "messages": state["messages"] + [AIMessage(content=f"")]
        }
    
    def _next_condition(self, state: TaskState) -> str:
        next_node = state.get("next_node")
        return next_node


    async def generate(self, user_input: str) -> XGATaskResult:
        result = None
        try:
            logging.info("****** Start React Agent for user_input: %s", user_input)

            # Create graph if not already created
            if self.graph is None:
                self.graph = await self._create_graph()

            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=f"information for: {user_input}")],
                "user_input": user_input,
                "next_node": None,
                "tasks": [],
                "context": "",
                "current_task": None,
                "next_task": None,
                "formatted_result": "",
                "final_error_info": "",
                "iteration_count": 1
            }

            # Run the retrieval graph with proper configuration
            config = {"recursion_limit": 100,
                      "configurable": {"thread_id": "manager_async_generate_thread"}}
            final_state = await self.graph.ainvoke(initial_state, config=config)

            # Parse and return formatted results
            result = final_state["formatted_result"]

            logging.info("=" * 100)
            logging.info("User question: %s", user_input)
            logging.info("User answer: %s", result)
            logging.info("=" * 100)

            return result
        except Exception as e:
            logging.error("### Error ManagerAgent _agent_work for user_input '%s': %s ###", user_input, str(e))
            handle_error(e)
            result = XGATaskResult(type="error", content="Never get result, Unexpected Error")
            return result


if __name__ == "__main__":
    setup_logging()

    agent = XGAReactAgent()
    user_inputs = [
                    "Create a function to sort a list of numbers, sort [6,8,7,5]"
                    , "sort [3,2,7,5]"
                ]
    for user_input in user_inputs:
        result = agent.generate(user_input)
        print(result)