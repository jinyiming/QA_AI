from langchain.tools import BaseTool
from typing import ClassVar, Dict,Any
import json
import sys
sys.path.append('./')
from file_rag.server.oa.api import flowCancle
class flowCancle_tool(BaseTool):

    name = "flowCancle"
    description = """
    涉及到撤办、撤回等操作，请使用此工具。
    从上下文获取总共有3个参数：文件标题：suject,令牌：token,是否确定：sure
    如不能直接获取到值，默认赋值为："否"禁止造词、造值。
    严格遵循工具描述内容，禁止造词、造值。
    """
    # parameters = {
    #     "type": "object",
    #     "properties": {
    #         "token": {
    #             "type": "string",
    #             "description": "令牌",
    #         },
    #           "subject": {
    #             "type": "string",
    #             "description": "文件名称、文件标题",
    #         },
    #           "sure": {
    #             "type": "string",
    #             "description": "是否确定要撤回",
    #         },
  
    #     "required": ["token","subject","sure"]
    #     }
    # }
    parameters: ClassVar[Dict[str, Any]] = {
        'type': 'object',
        'properties': {
            'token': {'type': 'string', 'description': '令牌'},
            'subject': {'type': 'string', 'description': '文件标题、文件名称'},
            'sure': {'type': 'string', 'description': '是否确认'},
            'required': ['token', 'subject', 'sure']
        },
        'description': "工具需要的参数"
        
    }
    def _run(self, token: str, subject: str , sure: str) -> str:
        print('欢迎使用【撤办】操作')    
        re = flowCancle.do_flowCancle_bysubject(token,subject,sure)
        return f'执行撤办的结果为：{re}'
        
    def _arun(self, query: str):
        raise NotImplementedError("This tool does not support async")