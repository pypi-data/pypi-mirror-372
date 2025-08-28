import asyncio

from xgae.engine.mcp_tool_box import XGAMcpToolBox
from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.llm_client import LLMConfig
from xgae.utils.misc import read_file

from xgae.utils.setup_env import setup_logging

setup_logging()

async def main() -> None:
    # Before Run Exec: uv run custom_fault_tools
    tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
    system_prompt = read_file("templates/example/fault_user_prompt.txt")

    engine = XGATaskEngine(tool_box=tool_box,
                           general_tools=[],
                           custom_tools=["*"],
                           llm_config=LLMConfig(stream=False),
                           system_prompt=system_prompt,
                           max_auto_run=8)

    user_input =  "locate 10.2.3.4 fault and solution"
    is_final_result = False

    if is_final_result:
        final_result = await engine.run_task_with_final_answer(task_message={"role": "user", "content": user_input})
        print("FINAL RESULT:", final_result)
    else:
        # Get All Task Process Message
        async for chunk in engine.run_task(task_message={"role": "user", "content": user_input}):
            print(chunk)

asyncio.run(main())