
import logging
import json
import os

from typing import List, Any, Dict, Optional, AsyncGenerator, Union, Literal
from uuid import uuid4

from xgae.engine.responser.responser_base import TaskResponserContext, TaskResponseProcessor, TaskRunContinuousState
from xgae.engine.engine_base import XGAResponseMsgType, XGAResponseMessage, XGAToolBox, XGATaskResult

from xgae.utils import handle_error
from xgae.utils.setup_env import langfuse

from xgae.utils.llm_client import LLMClient, LLMConfig, LangfuseMetadata

from xgae.utils.json_helpers import format_for_yield
from xgae.engine.prompt_builder import XGAPromptBuilder
from xgae.engine.mcp_tool_box import XGAMcpToolBox


class XGATaskEngine:
    def __init__(self,
                 session_id: Optional[str] = None,
                 task_id: Optional[str] = None,
                 agent_id: Optional[str] = None,
                 general_tools: Optional[List[str]] = None,
                 custom_tools: Optional[List[str]] = None,
                 system_prompt: Optional[str] = None,
                 max_auto_run: Optional[int] = None,
                 tool_exec_parallel: Optional[bool] = None,
                 llm_config: Optional[LLMConfig] = None,
                 prompt_builder: Optional[XGAPromptBuilder] = None,
                 tool_box: Optional[XGAToolBox] = None):
        self.task_id = task_id if task_id else f"xga_task_{uuid4()}"
        self.agent_id = agent_id
        self.session_id = session_id

        self.llm_client = LLMClient(llm_config)
        self.model_name = self.llm_client.model_name
        self.is_stream = self.llm_client.is_stream

        self.prompt_builder = prompt_builder or XGAPromptBuilder(system_prompt)
        self.tool_box: XGAToolBox = tool_box or XGAMcpToolBox()

        self.general_tools:List[str] = general_tools
        self.custom_tools:List[str] = custom_tools
        self.task_response_msgs: List[XGAResponseMessage] = []

        max_auto_run = max_auto_run if max_auto_run  else int(os.getenv("MAX_AUTO_RUN", 15))
        self.max_auto_run: int = 1 if max_auto_run <= 1 else max_auto_run
        self.tool_exec_parallel = True if tool_exec_parallel is None else tool_exec_parallel

        self.task_no = -1
        self.task_run_id :str = None

        self.task_prompt :str = None
        self.trace_id :str = None
        self.root_span_id :str = None
        self.root_span_name :str = None

    async def run_task_with_final_answer(self,
                                         task_message: Dict[str, Any],
                                         trace_id: Optional[str] = None) -> XGATaskResult:
        final_result:XGATaskResult = None
        try:
            self._init_langfuse("run_task_with_final_answer", task_message, trace_id)
            chunks = []
            async for chunk in self.run_task(task_message=task_message, trace_id=trace_id):
                chunks.append(chunk)

            if len(chunks) > 0:
                final_result = self._parse_final_result(chunks)
            else:
                final_result = XGATaskResult(type="error", content="LLM Answer is Empty")

            return final_result
        finally:
            self._end_langfuse("run_task_with_final_answer", final_result)


    async def run_task(self,
                       task_message: Dict[str, Any],
                       trace_id: Optional[str] = None) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            await self._init_task()
            self._init_langfuse("run_task", task_message, trace_id)

            self.add_response_message(type="user", content=task_message, is_llm_message=True)

            async for chunk in self._run_task_auto():
                yield chunk
        finally:
            await self.tool_box.destroy_task_tool_box(self.task_id)
            self._end_langfuse("run_task")


    async def _init_task(self) -> None:
        self.task_no = self.task_no + 1
        self.task_run_id = f"{self.task_id}[{self.task_no}]"

        general_tools = self.general_tools or ["complete", "ask"]
        if "*" not in general_tools:
            if "complete" not in general_tools:
                general_tools.append("complete")
            elif "ask" not in general_tools:
                general_tools.append("ask")

        custom_tools = self.custom_tools or []
        if isinstance(self.tool_box, XGAMcpToolBox):
            await  self.tool_box.load_mcp_tools_schema()

        await self.tool_box.creat_task_tool_box(self.task_id, general_tools, custom_tools)
        general_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "general_tool")
        custom_tool_schemas = self.tool_box.get_task_tool_schemas(self.task_id, "custom_tool")

        self.task_prompt = self.prompt_builder.build_task_prompt(self.model_name, general_tool_schemas, custom_tool_schemas)

        logging.info("*" * 30 + f"   XGATaskEngine Task'{self.task_id}' Initialized   " + "*" * 30)
        logging.info(f"model_name={self.model_name}, is_stream={self.is_stream}, trace_id={self.trace_id}")
        logging.info(f"general_tools={general_tools}, custom_tools={custom_tools}")


    async def _run_task_auto(self) -> AsyncGenerator[Dict[str, Any], None]:
        def update_continuous_state(_auto_continue_count,  _auto_continue):
            continuous_state["auto_continue_count"] = _auto_continue_count
            continuous_state["auto_continue"] = _auto_continue

        continuous_state: TaskRunContinuousState = {
            "accumulated_content": "",
            "auto_continue_count": 0,
            "auto_continue": False if self.max_auto_run <= 1 else True
        }

        auto_continue_count = 0
        auto_continue = True
        while auto_continue and auto_continue_count < self.max_auto_run:
            auto_continue = False

            try:
                async for chunk in self._run_task_once(continuous_state):
                    yield chunk
                    try:
                        if chunk.get("type") == "status":
                            content = json.loads(chunk.get('content', '{}'))
                            status_type = content.get('status_type', None)
                            if status_type == "error":
                                logging.error(f"run_task_auto: task_response error: {chunk.get('message', 'Unknown error')}")
                                auto_continue = False
                                break
                            elif status_type == 'finish':
                                finish_reason = content.get('finish_reason', None)
                                if finish_reason == 'completed':
                                    logging.info(f"run_task_auto: Detected finish_reason='completed', TASK_COMPLETE Success !")
                                    auto_continue = False
                                    break
                                elif finish_reason == 'xml_tool_limit_reached':
                                    logging.warning(f"run_task_auto: Detected finish_reason='xml_tool_limit_reached', stop auto-continue")
                                    auto_continue = False
                                    break
                                elif finish_reason == 'stop' or finish_reason == 'length': # 'length' never occur
                                    auto_continue = True
                                    auto_continue_count += 1
                                    update_continuous_state(auto_continue_count, auto_continue)
                                    logging.info(f"run_task_auto: Detected finish_reason='{finish_reason}', auto-continuing ({auto_continue_count}/{self.max_auto_run})")
                    except Exception as parse_error:
                        logging.error(f"run_task_auto: Error in parse chunk: {str(parse_error)}")
                        content = {"role": "system", "status_type": "error", "message": "Parse response chunk Error"}
                        handle_error(parse_error)
                        error_msg = self.add_response_message(type="status", content=content, is_llm_message=False)
                        yield format_for_yield(error_msg)
            except Exception as run_error:
                logging.error(f"run_task_auto: Call task_run_once error: {str(run_error)}")
                content = {"role": "system", "status_type": "error", "message": "Call task_run_once error"}
                handle_error(run_error)
                error_msg = self.add_response_message(type="status", content=content, is_llm_message=False)
                yield format_for_yield(error_msg)


    async def _run_task_once(self, continuous_state: TaskRunContinuousState) -> AsyncGenerator[Dict[str, Any], None]:
        llm_messages = [{"role": "system", "content": self.task_prompt}]
        cxt_llm_contents = self.get_history_llm_messages()
        llm_messages.extend(cxt_llm_contents)

        partial_content = continuous_state.get('accumulated_content', '')
        if partial_content:
            temp_assistant_message = {
                "role": "assistant",
                "content": partial_content
            }
            llm_messages.append(temp_assistant_message)

        llm_count = continuous_state.get("auto_continue_count")
        langfuse_metadata = self._create_llm_langfuse_meta(llm_count)
        llm_response = await self.llm_client.create_completion(llm_messages, langfuse_metadata)
        response_processor = self._create_response_processer()

        async for chunk in response_processor.process_response(llm_response, llm_messages, continuous_state):
            self._logging_reponse_chunk(chunk)
            yield chunk

    def _parse_final_result(self, chunks: List[Dict[str, Any]]) -> XGATaskResult:
        final_result: XGATaskResult = None
        try:
            finish_reason = ''
            for chunk in reversed(chunks):
                chunk_type = chunk.get("type")
                if chunk_type == "status":
                    status_content = json.loads(chunk.get('content', '{}'))
                    status_type = status_content.get('status_type', None)
                    if status_type == "error":
                        error = status_content.get('message', 'Unknown error')
                        final_result = XGATaskResult(type="error", content=error)
                    elif status_type == "finish":
                        finish_reason = status_content.get('finish_reason', None)
                        if finish_reason == 'xml_tool_limit_reached':
                            error = "Completed due to over task max_auto_run limit !"
                            final_result = XGATaskResult(type="error", content=error)
                elif chunk_type == "tool" and finish_reason in ['completed', 'stop']:
                    tool_content = json.loads(chunk.get('content', '{}'))
                    tool_execution = tool_content.get('tool_execution')
                    tool_name = tool_execution.get('function_name')
                    if tool_name == "complete":
                        result_content = tool_execution["arguments"].get("text", "Task completed with no answer")
                        attachments = tool_execution["arguments"].get("attachments", None)
                        final_result = XGATaskResult(type="answer", content=result_content, attachments=attachments)
                    elif tool_name == "ask":
                        result_content = tool_execution["arguments"].get("text", "Task ask for more info")
                        attachments = tool_execution["arguments"].get("attachments", None)
                        final_result = XGATaskResult(type="ask", content=result_content, attachments=attachments)
                    else:
                        tool_result = tool_execution.get("result", None)
                        if tool_result is not None:
                            success = tool_result.get("success")
                            output = tool_result.get("output")
                            result_type = "answer" if success else "error"
                            result_content = f"Task execute '{tool_name}' {result_type}: {output}"
                            final_result = XGATaskResult(type=result_type, content=result_content)
                elif chunk_type == "assistant" and finish_reason == 'stop':
                    assis_content = chunk.get('content', {})
                    result_content = assis_content.get("content", "LLM output is empty")
                    final_result = XGATaskResult(type="answer", content=result_content)

                if final_result is not None:
                    break
        except Exception as e:
            logging.error(f"parse_final_result: Final result pass error: {str(e)}")
            final_result = XGATaskResult(type="error", content="Parse final result failed!")
            handle_error(e)

        return final_result


    def add_response_message(self, type: XGAResponseMsgType,
                             content: Union[Dict[str, Any], List[Any], str],
                             is_llm_message: bool,
                             metadata: Optional[Dict[str, Any]]=None)-> XGAResponseMessage:
        metadata = metadata or {}
        metadata["task_id"] = self.task_id
        metadata["task_run_id"] = self.task_run_id
        metadata["trace_id"] = self.trace_id
        metadata["session_id"] = self.session_id
        metadata["agent_id"] = self.agent_id

        message = XGAResponseMessage(
            message_id = f"xga_msg_{uuid4()}",
            type = type,
            is_llm_message=is_llm_message,
            content = content,
            metadata = metadata
        )
        self.task_response_msgs.append(message)

        return message

    def get_history_llm_messages (self) -> List[Dict[str, Any]]:
        llm_messages = []
        for message in self.task_response_msgs:
            if message["is_llm_message"]:
                llm_messages.append(message)

        response_llm_contents = []
        for llm_message in llm_messages:
            content = llm_message["content"]
            # @todo content List type
            if isinstance(content, str):
                try:
                    _content = json.loads(content)
                    response_llm_contents.append(_content)
                except json.JSONDecodeError as e:
                    logging.error(f"get_context_llm_contents: Failed to decode json, content=:{content}")
                    handle_error(e)
            else:
                response_llm_contents.append(content)

        return response_llm_contents


    def _create_llm_langfuse_meta(self, llm_count:int)-> LangfuseMetadata:
        generation_name = f"xga_task_engine_llm_completion[{self.task_no}]({llm_count})"
        generation_id = f"{self.task_run_id}({llm_count})"
        return LangfuseMetadata(
            generation_name=generation_name,
            generation_id=generation_id,
            existing_trace_id=self.trace_id,
            session_id=self.session_id,
        )

    def _init_langfuse(self,
                       root_span_name: str,
                       task_message: Dict[str, Any],
                       trace_id: Optional[str] = None):

        if self.root_span_id is None:
            trace = None
            if trace_id:
                self.trace_id = trace_id
                trace = langfuse.trace(id=trace_id)
            else:
                trace = langfuse.trace(name="xga_task_engine")
                self.trace_id = trace.id

            span = trace.span(name=root_span_name, input=task_message,metadata={"task_id": self.task_id})
            self.root_span_id = span.id
            self.root_span_name = root_span_name

    def _end_langfuse(self, root_span_name:str, output: Optional[XGATaskResult]=None):
        if self.root_span_id and self.root_span_name == root_span_name:
            langfuse.span(trace_id=self.trace_id, id=self.root_span_id).end(output=output)
            self.root_span_id = None
            self.root_span_name = None

    def _create_response_processer(self) -> TaskResponseProcessor:
        response_context = self._create_response_context()
        is_stream = response_context.get("is_stream", False)
        if is_stream:
            from xgae.engine.responser.stream_responser import StreamTaskResponser
            return StreamTaskResponser(response_context)
        else:
            from xgae.engine.responser.non_stream_responser import NonStreamTaskResponser
            return NonStreamTaskResponser(response_context)

    def _create_response_context(self) -> TaskResponserContext:
        response_context: TaskResponserContext = {
            "is_stream": self.is_stream,
            "task_id": self.task_id,
            "task_run_id": self.task_run_id,
            "task_no": self.task_no,
            "trace_id": self.trace_id,
            "root_span_id": self.root_span_id,
            "model_name": self.model_name,
            "max_xml_tool_calls": 0,
            "add_response_msg_func": self.add_response_message,
            "tool_box": self.tool_box,
            "tool_execution_strategy": "parallel" if self.tool_exec_parallel else "sequential" ,#,
            "xml_adding_strategy": "user_message",
        }
        return response_context


    def _logging_reponse_chunk(self, chunk):
        chunk_type = chunk.get('type')
        prefix = ""

        if chunk_type == 'status':
            content = json.loads(chunk.get('content', '{}'))
            status_type = content.get('status_type', "empty")
            prefix = "-" + status_type
        elif chunk_type == 'tool':
            tool_content = json.loads(chunk.get('content', '{}'))
            tool_execution = tool_content.get('tool_execution')
            tool_name = tool_execution.get('function_name')
            prefix = "-" + tool_name

        logging.info(f"TASK_RESP_CHUNK[{chunk_type}{prefix}]: {chunk}")


if __name__ == "__main__":
    import asyncio
    from xgae.utils.misc import read_file

    async def main():
        tool_box = XGAMcpToolBox(custom_mcp_server_file="mcpservers/custom_servers.json")
        system_prompt = read_file("templates/example_user_prompt.txt")
        engine =  XGATaskEngine(tool_box=tool_box,
                                    general_tools=[],
                                    custom_tools=["*"],
                                    llm_config=LLMConfig(stream=False),
                                    system_prompt=system_prompt,
                                    max_auto_run=8)

        final_result = await engine.run_task_with_final_answer(task_message={"role": "user",
                                                                             "content": "locate 10.0.0.1 fault and solution"})
        print("FINAL RESULT:", final_result)


    asyncio.run(main())