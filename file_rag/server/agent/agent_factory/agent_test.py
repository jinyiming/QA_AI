import sys
sys.path.append('./')
from file_rag.server.oa.oa_tools import (get_OpinionInfo_tool,
                      get_userInfo_tool,
                      get_workflowInfo_tool,
                      get_DocList_tool,
                      get_FileContent_tool,
                      get_docStatistic_tool,
                    #   flowCancle_tool,
                    #   w_opinion_tool,
                      )
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .qwen_agent import create_structured_qwen_chat_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
import difflib

# 推理模型qwen
def _get_inLLM():
    return Ollama(base_url='http://localhost:11434',
                  model='qwen2:latest',
                  temperature=0.6)

def _get_llm_json():
    return ChatOllama(base_url='http://localhost:11434',model='qwen2:latest', format='json', temperature=0.6,)

# 公文列表
get_docList = get_DocList_tool.get_docList()
# 具体文件内容
get_fileContent = get_FileContent_tool.get_FileContent()
# 获取用户信息
get_userInfo = get_userInfo_tool.get_userInfo()
# 获取意见内容
get_opinionInfo = get_OpinionInfo_tool.get_OpinionInfo()
# 获取流程记录
get_workflowInfo = get_workflowInfo_tool.get_workflowInfo()
# 个人公文数量统计
get_docStatistic = get_docStatistic_tool.get_docStatistic()
# 撤办操作
# flowCancle = flowCancle_tool.flowCancle_tool()
# w_opinion = w_opinion_tool.w_opinion()

# 所需工具
# tools = [get_userInfo, get_fileContent, get_docList, get_opinionInfo, get_workflowInfo, get_docStatistic, flowCancle, w_opinion]

tools = [get_userInfo, get_fileContent, get_docList, get_opinionInfo, get_workflowInfo, get_docStatistic]


# 创建 agent
def get_promptTemplate_LLM():
    template = """
    {content}
    """ 
    custom_rag_prompt = PromptTemplate.from_template(template)
    return custom_rag_prompt

def get_oaAgentContext(query):
    callbacks = []
    print(query)
    content = query.split('|||')
    print(content)
    history = content[3]
    propmt = content[0]
    token = content[1]
    userid = content[2]
    systemNo = content[4]
    orgNo = content[5]

    # 定义与统计和报表相关的关键词
    keywords = ['报表', '统计']
    
    # 计算相似度
    def is_similar_to_keywords(text, keywords, threshold=0.6):
        for keyword in keywords:
            similarity = difflib.SequenceMatcher(None, text, keyword).ratio()
            if similarity > threshold:
                return True
        return False
    
    if is_similar_to_keywords(propmt, keywords):
        agent = create_structured_qwen_chat_agent(_get_llm_json(), tools, callbacks=callbacks, token=token, userId=userid, history=history, systemNo=systemNo, orgNo=orgNo)
    else:
        agent = create_structured_qwen_chat_agent(_get_inLLM(), tools, callbacks=callbacks, token=token, userId=userid, history=history, systemNo=systemNo, orgNo=orgNo)

    result = agent.invoke({"input": propmt})
    print("执行结果: ", result)

    return result

# if __name__ == "__main__":
#     get_oaAgentContext('待办文件')
