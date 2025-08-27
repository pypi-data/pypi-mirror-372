import asyncio

from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.llm_client import LLMConfig


async def main() -> None:
    engine =  XGATaskEngine(llm_config=LLMConfig(stream=False), max_auto_run=1)
    final_result = await engine.run_task_with_final_answer(task_message={"role": "user", "content": "1+1"})
    print("FINAL RESULT:", final_result)

asyncio.run(main())