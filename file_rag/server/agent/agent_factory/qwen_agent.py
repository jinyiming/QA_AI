from __future__ import annotations
from datetime import datetime
import json
import logging
import re
from typing import Dict
from functools import partial
from operator import itemgetter
from typing import Any, List, Sequence, Tuple, Union
import os
from langsmith import traceable
from langchain.memory import ConversationBufferMemory
from langchain.agents.agent import AgentExecutor, RunnableAgent
from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser
from langchain.prompts.chat import BaseChatPromptTemplate
from langchain.schema import (
    AgentAction,
    AgentFinish,
    AIMessage,
    HumanMessage,
    OutputParserException,
    SystemMessage,
)
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools.base import BaseTool
from langchain_core.callbacks import Callbacks
from langchain_core.runnables import Runnable, RunnablePassthrough

# os.environ['LANGCHAIN_TRACING_V2'] = 'true'

# os.environ['LANGCHAIN_API_KEY'] = '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'
# langchain's AgentRunnable use .stream to make sure .stream_log working.
# but qwen model cannot do tool call with streaming.
# patch it to make qwen lcel agent working


def _plan_without_stream(
    self: RunnableAgent,
    intermediate_steps: List[Tuple[AgentAction, str]],
    callbacks: Callbacks = None,
    **kwargs: Any,
) -> Union[AgentAction, AgentFinish]:
    inputs = {**kwargs, **{"intermediate_steps": intermediate_steps}}
    return self.runnable.invoke(inputs, config={"callbacks": callbacks})


async def _aplan_without_stream(
    self: RunnableAgent,
    intermediate_steps: List[Tuple[AgentAction, str]],
    callbacks: Callbacks = None,
    **kwargs: Any,
) -> Union[AgentAction, AgentFinish]:
    inputs = {**kwargs, **{"intermediate_steps": intermediate_steps}}
    return await self.runnable.ainvoke(inputs, config={"callbacks": callbacks})


class QwenChatAgentPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[BaseTool]
    token: str
    userId: str
    history: str
    systemNo: str
    orgNo: str

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps", [])
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        if thoughts:
            kwargs[
                "agent_scratchpad"
            ] = f"These were previous tasks you completed:\n{thoughts}\n\n"
        else:
            kwargs["agent_scratchpad"] = ""
        # Create a tools variable from the list of tools provided

        tools = []
        for t in self.tools:
            desc = re.sub(r"\n+", " ", t.description)
            text = (
                f"{t.name}: Call this tool to interact with the {
                    t.name} API. What is the {t.name} API useful for?"
                f" {desc}"
                f" Parameters: {t.args}"
            )
            tools.append(text)
        kwargs["tools"] = "\n\n".join(tools)
        # kwargs["tools"] = "\n".join([str(format_tool_to_openai_function(tool)) for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        kwargs["userId"] = self.userId
        kwargs["token"] = self.token
        now = datetime.now()
        current_date = now.date()
        kwargs["today"] = current_date
        # {chat_history}
        kwargs["chat_history"] = self.history
        kwargs["systemNo"] = self.systemNo
        kwargs["orgNo"] = self.orgNo
        formatted = self.template.format(**kwargs)
        return [SystemMessage(content=formatted)]


def validate_json(json_data: str):
    try:
        json.loads(json_data)
        return True
    except ValueError:
        return False


class QwenChatAgentOutputParserCustom(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with custom qwen prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if s := re.findall(
            r"\nAction:\s*(.+)\nAction\sInput:\s*(.+)", text, flags=re.DOTALL
        ):
            s = s[-1]
            json_string: str = s[1]
            json_input = None
            try:
                json_input = json.loads(json_string)
            except:
                # ollama部署的qwen，返回的json键值可能为单引号，可能缺少最后的引号和括号
                if not json_string.endswith('"}'):
                    print("缺少单括号，尝试修复格式不正确的json输出:" + json_string)
                    fixed_json_string = (json_string + '}').replace("'", '"')
                    print(f'第一步修正单括号之后的json{fixed_json_string}')
                    fixed = True
                    if not validate_json(fixed_json_string):
                        # ollama部署的qwen，返回的json可能有注释，需要去掉注释
                        fixed_json_string = (re.sub(r'//.*', '', (json_string + '"}').replace("'", '"'))
                                             .strip()
                                             .replace('\n', ''))
                        fixed_json_string = (re.sub(r'#.*', '', (json_string + '"}').replace("'", '"'))
                                             .strip()
                                             .replace('\n', ''))
                        print(f'第二步修正单括号、去掉之后的json{fixed_json_string}')
                        if not validate_json(fixed_json_string):
                            fixed = False
                            print("尝试修复json格式失败：" + fixed_json_string)
                    if fixed:
                        json_string = fixed_json_string
                        print("修复后的json输出:" + json_string)

                    json_input = json.loads(json_string)
            # 有概率key为command而非query，需修改
            if "command" in json_input:
                json_input["query"] = json_input.pop("command")
            return AgentAction(tool=s[0].strip(), tool_input=json_input, log=text)
        elif s := re.findall(r"\nFinal\sAnswer:\s*(.+)", text, flags=re.DOTALL):
            s = s[-1]
            return AgentFinish({"output": s}, log=text)
        else:
            return AgentFinish({"output": text}, log=text)
            # raise OutputParserException(f"Could not parse LLM output: {text}")

    @property
    def _type(self) -> str:
        return "StructuredQWenChatOutputParserCustom"


class QwenChatAgentOutputParserLC(StructuredChatOutputParser):
    """Output parser with retries for the structured chat agent with standard lc prompt."""

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        if s := re.findall(r"\nAction:\s*```(.+)```", text, flags=re.DOTALL):
            action = json.loads(s[0])
            tool = action.get("action")
            if tool == "Final Answer":
                return AgentFinish({"output": action.get("action_input", "")}, log=text)
            else:
                return AgentAction(
                    tool=tool, tool_input=action.get("action_input", {}), log=text
                )
        else:
            raise OutputParserException(f"Could not parse LLM output: {text}")

    @property
    def _type(self) -> str:
        return "StructuredQWenChatOutputParserLC"


class CustomAgentExecutor(AgentExecutor):
    def _execute(self, *args, **kwargs) -> Dict[str, Any]:
        result = super()._execute(*args, **kwargs)
        # 假设 result 包含 'final_answer' 和 'intermediate_steps'
        raw_results = {}
        for step in result.get('intermediate_steps', []):
            action, observation = step
            raw_results[action.tool] = observation
        return {
            "final_answer": result.get("final_answer"),
            "raw_results": raw_results
        }


def create_structured_qwen_chat_agent(
    llm: BaseLanguageModel,
    tools: Sequence[BaseTool],
    token: str,
    userId: str,
    history: str,
    systemNo: str,
    orgNo: str,
    callbacks: Sequence[Callbacks],
    use_custom_prompt: bool = True,
) -> CustomAgentExecutor:  # 修改返回类型为 CustomAgentExecutor
    if use_custom_prompt:
        prompt = "qwen"
        output_parser = QwenChatAgentOutputParserCustom()
    else:
        prompt = "structured-chat-agent"
        output_parser = QwenChatAgentOutputParserLC()

    tools = [t.copy(update={"callbacks": callbacks}) for t in tools]
    
    template = """
     "
     Today is {today}, 'token' is {token}, userId is {userId}, systemNo is {systemNo}, orgNo is {orgNo}
     Answer the following questions as best you can. You have access to the following APIs:\n\n"
            "{tools}\n\n"
            
            These are chat history before:
            {chat_history}
            
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            "Action: the action to take, should be one of [{tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
           
            "... (this Thought/Action/Action Input/Observation/Reflection can be repeated zero or more times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Format the Action Input as a JSON object.\n\n"
            "Begin!\n\n"
            "Question: {input}\n\n"
            "{agent_scratchpad}\n\n"
    """
    #  "Reflection: evaluate the result of the action and consider next steps\n"
    prompt = QwenChatAgentPromptTemplate(
        input_variables=["input", "intermediate_steps"], template=template, tools=tools, token=token, userId=userId, history=history
    , systemNo=systemNo, orgNo=orgNo)
    print(prompt)
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=itemgetter("intermediate_steps"))
        | prompt
        | llm.bind(
            stop=["<|endoftext|>", "<|im_start|>",
                  "<|im_end|>", "\nObservation:"]
        )
        | output_parser
    )
    
    memory = ConversationBufferMemory(memory_key="chat_history")
    executor = CustomAgentExecutor(  # 使用自定义的Executor
        agent=agent, 
        tools=tools,
        callbacks=callbacks, 
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        early_stopping_method="generate",
        return_intermediate_steps=True,
        memory=memory
    )
    
 
    
    executor.agent.__dict__["plan"] = partial(
        _plan_without_stream, executor.agent)
    executor.agent.__dict__["aplan"] = partial(
        _aplan_without_stream, executor.agent)

    return executor
