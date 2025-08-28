import asyncio

from xgae.engine.task_engine import XGATaskEngine
from xgae.utils.llm_client import LLMConfig

from xgae.utils.setup_env import setup_logging

setup_logging()

async def main() -> None:
    engine =  XGATaskEngine(llm_config=LLMConfig(stream=False), max_auto_run=3)

    final_result = await engine.run_task_with_final_answer(
        task_message={"role": "user", "content": "1+7"}
    )

    print("FINAL RESULT:", final_result)


asyncio.run(main())