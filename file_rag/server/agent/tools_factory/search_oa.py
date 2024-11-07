import sys
sys.path.append('./')

from pydantic.v1 import Field
from file_rag.server.agent.tools_factory.tools_registry import (
    BaseToolOutput,
    regist_tool,
)
from file_rag.server.agent.agent_factory.agent_test import get_oaAgentContext
from langchain_community.llms import Ollama



def search_o(query: str):
    docs = get_oaAgentContext(query)
    return docs


@regist_tool(title="OA系统")
def search_oa(
    query: str = Field(description="输入关于OA系统相关的问题"),
) -> str:
    """
    OA for Knowledge Search
    """
    # print(query)
    content = query.split('|||')
    print(content)
    propmt = content[0]
    # token = content[1]
    # userid = content[2]
    docs = get_oaAgentContext(query)
    # {'input': 'token=6cebf1db-37c7-48a9-9fff-51bb4d27265b,userid=U004952,我的个人信息', 
    # 'output': 'Final Answer: 用户ID为U004952的个人信息如下：\n\n- 姓名：任佳雨\n- 手机号：19945060117\n- 邮箱地址：renjiayu@xy.zw\n- 所在单位：市大数据中心，项目一部\n- 单位归属：/襄阳市/市数据局/市大数据中心/项目一部\n- 加入时间：2017-09-01\n- 最近登录时间：2024年9月10日 09:15:47\n- 简称：renjiayu\n- OA系统ID：XYSSJJ\n\n请记住，这些信息可能会随着用户数据的更新而变化。如果需要获取最新的个人信息，请使用提供的工具或直接联系管理员。'}
    docs['input'] = propmt
    docs['output'] = docs['output'].replace('Final Answer','')
    result = {}
    # result['context'] = docs['output'] 
    print(f'---------------{docs['intermediate_steps']}')
    if docs['intermediate_steps']:
        result['data'] = docs['intermediate_steps'][0][1]
    print(f'最后一层 模型的输入为：{result}')
    return BaseToolOutput(result, format='json')
