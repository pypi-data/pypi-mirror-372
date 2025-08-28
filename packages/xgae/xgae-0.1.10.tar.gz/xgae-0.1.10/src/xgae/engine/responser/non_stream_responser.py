import logging

from typing import List, Dict, Any, AsyncGenerator, override,Optional
from xgae.utils.json_helpers import format_for_yield

from xgae.engine.responser.responser_base import TaskResponseProcessor, TaskResponserContext, TaskRunContinuousState


class NonStreamTaskResponser(TaskResponseProcessor):
    def __init__(self, response_context: TaskResponserContext):
        super().__init__(response_context)

    @override
    async def process_response(self,llm_response: Any,prompt_messages: List[Dict[str, Any]],
                               continuous_state: Optional[TaskRunContinuousState] = None) -> AsyncGenerator[Dict[str, Any], None]:
        llm_content = ""
        parsed_xml_data = []
        finish_reason = None
        llm_count = continuous_state.get("auto_continue_count")

        try:
            # Extract finish_reason, content, tool calls
            if hasattr(llm_response, 'choices') and llm_response.choices:
                if hasattr(llm_response.choices[0], 'finish_reason'):
                    finish_reason = llm_response.choices[0].finish_reason
                    logging.info(f"NonStreamTask：LLM response finish_reason={finish_reason}")

                    self.root_span.event(name=f"non_stream_processor_start[{self.task_no}]({llm_count})", level="DEFAULT",
                                     status_message=(f"finish_reason={finish_reason}, tool_exec_strategy={self.tool_execution_strategy}"))

                response_message = llm_response.choices[0].message if hasattr(llm_response.choices[0], 'message') else None
                if response_message:
                    if hasattr(response_message, 'content') and response_message.content:
                        llm_content = response_message.content
                        
                        parsed_xml_data = self._parse_xml_tool_calls(llm_content)
                        if self.max_xml_tool_calls > 0 and len(parsed_xml_data) > self.max_xml_tool_calls:
                            logging.warning(f"NonStreamTask：Truncate content, parsed_xml_data length {len(parsed_xml_data)} limit over max_xml_tool_calls={self.max_xml_tool_calls}")
                            xml_chunks = self._extract_xml_chunks(llm_content)[:self.max_xml_tool_calls]
                            if xml_chunks:
                                last_chunk = xml_chunks[-1]
                                last_chunk_pos = llm_content.find(last_chunk)
                                if last_chunk_pos >= 0:
                                    llm_content = llm_content[:last_chunk_pos + len(last_chunk)]
                            parsed_xml_data = parsed_xml_data[:self.max_xml_tool_calls]
                            finish_reason = "xml_tool_limit_reached"
                            logging.info(f"NonStreamTask：LLM response finish_reason={finish_reason}")
                else:
                    logging.warning(f"NonStreamTask：LLM response_message is empty")

            message_data = {"role": "assistant", "content": llm_content} # index=-1, full llm_content
            assistant_msg = self.add_response_message(type="assistant_complete", content=message_data, is_llm_message=True)
            yield assistant_msg

            tool_calls_to_execute = [item['tool_call'] for item in parsed_xml_data]
            if  len(tool_calls_to_execute) > 0:
                logging.info(f"NonStreamTask：Executing {len(tool_calls_to_execute)} tools with strategy: {self.tool_execution_strategy}")

                tool_results = await self._execute_tools(tool_calls_to_execute, self.tool_execution_strategy)

                tool_index = 0
                for i, (returned_tool_call, tool_result) in enumerate(tool_results):
                    parsed_xml_item = parsed_xml_data[i]
                    tool_call = parsed_xml_item['tool_call']
                    parsing_details = parsed_xml_item['parsing_details']
                    assistant_msg_id = assistant_msg['message_id'] if assistant_msg else None

                    tool_context = self._create_tool_context(tool_call, tool_index, assistant_msg_id, parsing_details)
                    tool_context.result = tool_result

                    tool_start_msg = self._add_tool_start_message(tool_context)
                    yield format_for_yield(tool_start_msg)

                    tool_message = self._add_tool_messsage(tool_call, tool_result, self.xml_adding_strategy, assistant_msg_id, parsing_details)

                    tool_completed_msg = self._add_tool_completed_message(tool_context, tool_message['message_id'])
                    yield format_for_yield(tool_completed_msg)

                    yield format_for_yield(tool_message)

                    if tool_completed_msg["metadata"].get("agent_should_terminate") == "true":
                        finish_reason = "completed"
                        break
                    tool_index += 1
            else:
                finish_reason = "non_tool_call"
                logging.warning(f"NonStreamTask: tool_calls is empty, No Tool need to call !")

            if finish_reason:
                finish_content = {"status_type": "finish", "finish_reason": finish_reason}
                finish_msg_obj = self.add_response_message(type="status", content=finish_content, is_llm_message=False)
                if finish_msg_obj:
                    yield format_for_yield(finish_msg_obj)

        except Exception as e:
            logging.error(f"NonStreamTask: Error processing non-streaming response: {llm_content}")
            self.root_span.event(name="error_processing_non_streaming_response", level="ERROR",
                             status_message=(f"Error processing non-streaming response: {str(e)}"))

            content = {"role": "system", "status_type": "error", "message": str(e)}
            err_msg = self.add_response_message(ype="status", content=content,is_llm_message=False)
            if err_msg:
                yield format_for_yield(err_msg)

            # Re-raise the same exception (not a new one) to ensure proper error propagation
            logging.critical(f"NonStreamTask: Re-raising error to stop further processing: {str(e)}")
            self.root_span.event(name="re_raising_error_to_stop_further_processing", level="CRITICAL",
                             status_message=(f"Re-raising error to stop further processing: {str(e)}"))
            raise  # Use bare 'raise' to preserve the original exception with its traceback



