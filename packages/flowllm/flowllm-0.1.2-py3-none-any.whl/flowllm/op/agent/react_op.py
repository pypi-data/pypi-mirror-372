import datetime
import time
from typing import List, Dict

from loguru import logger

from flowllm import C, BaseLLMOp
from flowllm.flow.base_tool_flow import BaseToolFlow
from flowllm.flow.gallery import DashscopeSearchToolFlow, CodeToolFlow, TerminateToolFlow
from flowllm.schema.message import Message, Role


@C.register_op()
class ReactOp(BaseLLMOp):
    # TODO: test react op
    file_path: str = __file__

    def execute(self):
        query: str = self.context.query

        max_steps: int = int(self.op_params.get("max_steps", 10))
        tools: List[BaseToolFlow] = [DashscopeSearchToolFlow(), CodeToolFlow(), TerminateToolFlow()]
        tool_dict: Dict[str, BaseToolFlow] = {x.name: x for x in tools}
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        has_terminate_tool = False

        user_prompt = self.prompt_format(prompt_name="role_prompt",
                                         time=now_time,
                                         tools=",".join([x.name for x in tools]),
                                         query=query)
        messages: List[Message] = [Message(role=Role.USER, content=user_prompt)]
        logger.info(f"step.0 user_prompt={user_prompt}")

        for i in range(max_steps):
            if has_terminate_tool:
                assistant_message: Message = self.llm.chat(messages)
            else:
                assistant_message: Message = self.llm.chat(messages, tools=[x.tool_call for x in tools])

            messages.append(assistant_message)
            logger.info(f"assistant.{i}.reasoning_content={assistant_message.reasoning_content}\n"
                        f"content={assistant_message.content}\n"
                        f"tool.size={len(assistant_message.tool_calls)}")

            if has_terminate_tool:
                break

            for tool in assistant_message.tool_calls:
                if tool.name == "terminate":
                    has_terminate_tool = True
                    logger.info(f"step={i} find terminate tool, break.")
                    break

            if not has_terminate_tool and not assistant_message.tool_calls:
                logger.warning(f"【bugfix】step={i} no tools, break.")
                has_terminate_tool = True

            for j, tool_call in enumerate(assistant_message.tool_calls):
                logger.info(f"submit step={i} tool_calls.name={tool_call.name} argument_dict={tool_call.argument_dict}")

                if tool_call.name not in tool_dict:
                    continue

                self.submit_task(tool_dict[tool_call.name].__call__, **tool_call.argument_dict)
                time.sleep(1)

            if not has_terminate_tool:
                user_content_list = []
                for tool_result, tool_call in zip(self.join_task(), assistant_message.tool_calls):
                    logger.info(f"submit step={i} tool_calls.name={tool_call.name} tool_result={tool_result}")
                    assert isinstance(tool_result, str)
                    user_content_list.append(f"<tool_response>\n{tool_result}\n</tool_response>")
                user_content_list.append(self.prompt_format(prompt_name="next_prompt"))
                assistant_message.tool_calls.clear()
                messages.append(Message(role=Role.USER, content="\n".join(user_content_list)))

            else:
                assistant_message.tool_calls.clear()
                messages.append(Message(role=Role.USER, content=self.prompt_format(prompt_name="final_prompt")))

        # Store results in context instead of response
        self.context.messages = messages
        self.context.answer = messages[-1].content
