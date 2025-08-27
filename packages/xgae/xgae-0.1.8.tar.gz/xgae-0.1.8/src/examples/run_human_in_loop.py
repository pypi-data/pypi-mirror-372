import asyncio

from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.llm_client import LLMConfig
from xgae.utils.misc import read_file


async def main() -> None:
    tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
    system_prompt = read_file("templates/example_user_prompt.txt")
    engine = XGATaskEngine(tool_box=tool_box,
                           general_tools=[],
                           custom_tools=["*"],
                           llm_config=LLMConfig(stream=False),
                           system_prompt=system_prompt,
                           max_auto_run=8)

    user_input =  "locate fault and solution"
    final_result = await engine.run_task_with_final_answer(task_message={"role": "user", "content": user_input})
    print("FINAL RESULT:", final_result)

    if final_result["type"] == "ask":
        print("====== Wait for user input ... ======")
        user_input = "ip=10.0.1.1"
        final_result = await engine.run_task_with_final_answer(task_message={"role": "user", "content": user_input})
        print("FINAL RESULT:", final_result)

asyncio.run(main())